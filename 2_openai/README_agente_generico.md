# 🤖 Agente Genérico Reutilizable

Un agente de IA genérico y reutilizable que se puede instanciar en cualquier parte de tu aplicación. Soporta múltiples proveedores de modelos y herramientas personalizables.

## 🚀 Características

- **Multi-proveedor**: Soporta OpenRouter, OpenAI y proveedores personalizados
- **Reutilizable**: Instancia el agente en cualquier archivo o módulo
- **Configurable**: Personaliza nombre, instrucciones y herramientas
- **Dinámico**: Añade/elimina herramientas y actualiza instrucciones en tiempo real
- **Fácil de usar**: API simple e intuitiva

## 📋 Requisitos

```bash
pip install openai agents
```

## 🔑 Configuración de Variables de Entorno

```bash
# Para OpenRouter (por defecto)
export OPEN_ROUTER_API_KEY="tu-api-key-de-openrouter"

# Para OpenAI
export OPENAI_API_KEY="tu-api-key-de-openai"
```

## 💻 Uso Básico

### 1. Importar y crear un agente

```python
from generic_agent import create_agent

# Agente básico
agente = create_agent(
    name="MiAgente",
    instructions="Eres un asistente útil."
)

# Usar el agente
resultado = await agente.run("Hola, ¿cómo estás?")
print(resultado.final_output)
```

### 2. Agente con herramientas específicas

```python
from generic_agent import create_agent, get_weather, calculate

agente_clima = create_agent(
    name="Meteorologo",
    instructions="Eres un experto en clima.",
    tools=[get_weather, calculate]
)

resultado = await agente_clima.run("¿Cómo está el clima en Madrid?")
```

### 3. Agente con proveedor específico

```python
# Usar OpenAI directamente
agente_openai = create_agent(
    name="AgenteOpenAI",
    instructions="Eres un asistente de OpenAI.",
    model_provider="openai"
)

# Usar OpenRouter (por defecto)
agente_openrouter = create_agent(
    name="AgenteOpenRouter",
    instructions="Eres un asistente de OpenRouter.",
    model_provider="openrouter"
)
```

## 🛠️ Herramientas Disponibles

### Herramientas incluidas:

- `get_weather(city)`: Obtiene información del clima
- `calculate(expression)`: Calcula expresiones matemáticas
- `get_time()`: Obtiene la hora actual

### Crear herramientas personalizadas:

```python
from generic_agent import function_tool

@function_tool
def mi_herramienta(parametro: str) -> str:
    """Descripción de mi herramienta"""
    return f"Resultado: {parametro}"

# Usar en un agente
agente = create_agent(
    name="AgentePersonalizado",
    tools=[mi_herramienta]
)
```

## 🔧 API Completa

### Clase GenericAgent

```python
from generic_agent import GenericAgent

agente = GenericAgent(
    name="Nombre del Agente",
    instructions="Instrucciones del agente",
    tools=[lista_de_herramientas],
    model_provider="openrouter",  # "openrouter", "openai", "custom"
    model_name="gpt-4o-mini",
    api_key="tu-api-key",
    base_url="https://api.openai.com/v1"
)
```

### Métodos disponibles:

- `run(message)`: Ejecuta el agente con un mensaje
- `add_tool(tool)`: Añade una herramienta
- `update_instructions(new_instructions)`: Actualiza las instrucciones
- `get_info()`: Obtiene información del agente

## 📚 Ejemplos de Uso

### En un script simple:

```python
import asyncio
from generic_agent import create_agent

async def main():
    agente = create_agent(
        name="Asistente",
        instructions="Eres un asistente amigable."
    )
    
    resultado = await agente.run("Hola!")
    print(resultado.final_output)

asyncio.run(main())
```

### En una clase:

```python
class MiAplicacion:
    def __init__(self):
        self.agente = create_agent(
            name="AgenteApp",
            instructions="Eres un asistente de aplicación."
        )
    
    async def procesar_consulta(self, consulta: str):
        resultado = await self.agente.run(consulta)
        return resultado.final_output

# Usar
app = MiAplicacion()
respuesta = await app.procesar_consulta("¿Qué puedes hacer?")
```

### En un módulo:

```python
# mi_modulo.py
from generic_agent import create_agent

class MiModulo:
    def __init__(self):
        self.agente = create_agent(
            name="ModuloAgente",
            instructions="Eres un agente especializado en este módulo."
        )
    
    async def ejecutar_tarea(self, tarea: str):
        return await self.agente.run(tarea)

# En otro archivo
from mi_modulo import MiModulo

modulo = MiModulo()
resultado = await modulo.ejecutar_tarea("Mi tarea")
```

## 🌟 Casos de Uso Comunes

1. **Chatbots**: Crear asistentes conversacionales
2. **Análisis de datos**: Agentes especializados en procesamiento
3. **Automatización**: Agentes que ejecutan tareas específicas
4. **Educación**: Tutores y asistentes de aprendizaje
5. **Soporte**: Agentes de atención al cliente

## ⚠️ Consideraciones

- **Async/Await**: El agente es asíncrono, usa `async/await` o `asyncio.run()`
- **API Keys**: Configura las variables de entorno apropiadas
- **Rate Limiting**: Respeta los límites de tu proveedor de API
- **Costos**: Monitorea el uso de tokens para controlar costos

## 🚨 Solución de Problemas

### Error: "API key no está configurado"
```bash
export OPEN_ROUTER_API_KEY="tu-api-key"
# o
export OPENAI_API_KEY="tu-api-key"
```

### Error: "Proveedor de modelo no soportado"
```python
# Usa uno de estos valores:
model_provider="openrouter"  # Por defecto
model_provider="openai"
model_provider="custom"
```

### Error: "ModuleNotFoundError: No module named 'agents'"
```bash
pip install agents
```

## 📖 Archivos del Proyecto

- `generic_agent.py`: Clase principal del agente genérico
- `config_agente.py`: Sistema de configuración
- `README_agente_generico.md`: Esta documentación

## 🚀 **Ejecutar Ejemplos**

```bash
# Ejecutar ejemplo básico
python generic_agent.py

# Verificar configuración
python config_agente.py
```

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Si encuentras un bug o tienes una sugerencia, abre un issue o envía un pull request.

## 📄 Licencia

Este proyecto está bajo la misma licencia que el proyecto principal.
