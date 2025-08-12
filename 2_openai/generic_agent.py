import asyncio
import os
from typing import List, Optional, Dict, Any, Union
from openai import AsyncOpenAI

from agents import (
    Agent,
    Model,
    ModelProvider,
    OpenAIChatCompletionsModel,
    RunConfig,
    Runner,
    function_tool,
)

class GenericAgent:
    """
    Agente genérico y reutilizable que se puede instanciar en cualquier parte.
    Soporta múltiples proveedores de modelos y herramientas personalizables.
    """
    
    def __init__(
        self,
        name: str = "GenericAgent",
        instructions: str = "Eres un asistente útil y amigable.",
        tools: Optional[List] = None,
        model_provider: Optional[str] = "openrouter",  # "openrouter", "openai", "custom"
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self.model_provider = model_provider
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key
        # Inicializar el agente
        self._setup_agent()
    
    def _setup_agent(self):
        """Configura el agente con el proveedor de modelo apropiado"""
        # Configurar el proveedor de modelo
        if self.model_provider == "openrouter":
            self._setup_openrouter()
        elif self.model_provider == "openai":
            self._setup_openai()
        elif self.model_provider == "custom":
            self._setup_custom()
        else:
            raise ValueError(f"Proveedor de modelo no soportado: {self.model_provider}")
        
        # Crear el agente
        self.agent = Agent(
            name=self.name,
            instructions=self.instructions,
            tools=self.tools
        )
    
    def _setup_openrouter(self):
        """Configura OpenRouter como proveedor de modelo"""
        self.base_url = self.base_url or "https://openrouter.ai/api/v1"
        self.api_key = self.api_key or os.getenv("OPEN_ROUTER_API_KEY")
        self.model_name = self.model_name or "openai/gpt-4o-mini"
        
        if not self.api_key:
            raise ValueError("OPEN_ROUTER_API_KEY no está configurado")
        
        client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)
        self.model_provider_instance = OpenRouterModelProvider(client, self.model_name)
    
    def _setup_openai(self):
        """Configura OpenAI como proveedor de modelo"""
        self.api_key = self.api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = self.model_name or "gpt-4o-mini"
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY no está configurado")
        
        client = AsyncOpenAI(api_key=self.api_key)
        self.model_provider_instance = OpenAIModelProvider(client, self.model_name)
    
    def _setup_custom(self):
        """Configura un proveedor de modelo personalizado"""
        if not all([self.base_url, self.api_key, self.model_name]):
            raise ValueError("Para proveedor personalizado, debes especificar base_url, api_key y model_name")
        
        client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)
        self.model_provider_instance = OpenAIModelProvider(client, self.model_name)
    
    async def run(self, message: str, **kwargs) -> Any:
        """
        Ejecuta el agente con un mensaje
        
        Args:
            message: El mensaje o pregunta para el agente
            **kwargs: Argumentos adicionales para Runner.run()
        
        Returns:
            El resultado de la ejecución del agente
        """
        run_config = RunConfig(model_provider=self.model_provider_instance)
        
        result = await Runner.run(
            self.agent,
            message,
            run_config=run_config,
            **kwargs
        )
        
        return result
    
    def add_tool(self, tool):
        """Añade una herramienta al agente"""
        self.tools.append(tool)
        # Recrear el agente con las nuevas herramientas
        self.agent = Agent(
            name=self.name,
            instructions=self.instructions,
            tools=self.tools
        )
    
    def update_instructions(self, new_instructions: str):
        """Actualiza las instrucciones del agente"""
        self.instructions = new_instructions
        # Recrear el agente con las nuevas instrucciones
        self.agent = Agent(
            name=self.name,
            instructions=self.instructions,
            tools=self.tools
        )
    
    def get_info(self) -> Dict[str, Any]:
        """Obtiene información del agente"""
        return {
            "name": self.name,
            "instructions": self.instructions,
            "tools_count": len(self.tools),
            "model_provider": self.model_provider,
            "model_name": self.model_name
        }


class OpenRouterModelProvider(ModelProvider):
    """Proveedor de modelo para OpenRouter"""
    
    def __init__(self, client: AsyncOpenAI, model_name: str):
        self.client = client
        self.model_name = model_name
    
    def get_model(self, model_name: str | None) -> Model:
        return OpenAIChatCompletionsModel(
            model=model_name or self.model_name,
            openai_client=self.client
        )


class OpenAIModelProvider(ModelProvider):
    """Proveedor de modelo para OpenAI"""
    
    def __init__(self, client: AsyncOpenAI, model_name: str):
        self.client = client
        self.model_name = model_name
    
    def get_model(self, model_name: str | None) -> Model:
        return OpenAIChatCompletionsModel(
            model=model_name or self.model_name,
            openai_client=self.client
        )


# Herramientas de ejemplo que puedes usar
@function_tool
def get_weather(city: str) -> str:
    """Obtiene el clima de una ciudad"""
    return f"El clima en {city} es soleado y agradable."

@function_tool
def calculate(expression: str) -> str:
    """Calcula una expresión matemática"""
    try:
        result = eval(expression)
        return f"El resultado de {expression} es {result}"
    except Exception as e:
        return f"Error al calcular {expression}: {str(e)}"

@function_tool
def get_time() -> str:
    """Obtiene la hora actual"""
    from datetime import datetime
    return f"La hora actual es {datetime.now().strftime('%H:%M:%S')}"


# Función de conveniencia para crear agentes rápidamente
def create_agent(
    name: str = "GenericAgent",
    instructions: str = "Eres un asistente útil y amigable.",
    tools: Optional[List] = None,
    model_provider: str = "openrouter",
    **kwargs
) -> GenericAgent:
    """
    Función de conveniencia para crear agentes rápidamente
    
    Args:
        name: Nombre del agente
        instructions: Instrucciones del agente
        tools: Lista de herramientas
        model_provider: Proveedor de modelo ("openrouter", "openai", "custom")
        **kwargs: Argumentos adicionales para GenericAgent
    
    Returns:
        Una instancia de GenericAgent
    """
    # Preparar argumentos para GenericAgent
    agent_kwargs = {
        "name": name,
        "instructions": instructions,
        "tools": tools,
        "model_provider": model_provider
    }
    
    # Añadir argumentos adicionales si están presentes
    for key, value in kwargs.items():
        if key in ["model_name", "api_key", "base_url"]:
            agent_kwargs[key] = value
    
    return GenericAgent(**agent_kwargs)


# Ejemplo de uso
if __name__ == "__main__":
    async def example():
        print("=== Ejemplo de Agente Genérico ===")
        
        # Crear un agente básico
        agente1 = create_agent(
            name="AgenteClima",
            instructions="Eres un experto en clima que responde en español.",
            tools=[get_weather]
        )
        
        # Crear un agente matemático
        agente2 = create_agent(
            name="AgenteMatematico",
            instructions="Eres un experto en matemáticas que resuelve problemas.",
            tools=[calculate],
            model_provider="openai"  # Usar OpenAI directamente
        )
        
        # Usar los agentes
        print("=== Agente del Clima ===")
        result1 = await agente1.run("¿Cómo está el clima en Madrid?")
        print(result1.final_output)
        
        print("\n=== Agente Matemático ===")
        result2 = await agente2.run("Calcula 15 * 8 + 23")
        print(result2.final_output)
    
    asyncio.run(example())
