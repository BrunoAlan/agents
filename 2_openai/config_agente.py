"""
Archivo de configuración para el agente genérico
"""

import os
from typing import Dict, Any

# Configuraciones por defecto
DEFAULT_CONFIG = {
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model_name": "openai/gpt-4o-mini",
        "env_key": "OPEN_ROUTER_API_KEY"
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY"
    }
}

# Configuraciones personalizadas
CUSTOM_CONFIGS = {
    "agente_clima": {
        "name": "Meteorologo",
        "instructions": "Eres un experto meteorólogo que responde en español.",
        "model_provider": "openrouter",
        "tools": ["get_weather", "get_time"]
    },
    "agente_math": {
        "name": "Matematico",
        "instructions": "Eres un experto en matemáticas que resuelve problemas paso a paso.",
        "model_provider": "openai",
        "tools": ["calculate"]
    },
    "agente_general": {
        "name": "AsistenteGeneral",
        "instructions": "Eres un asistente amigable y útil que responde en español.",
        "model_provider": "openrouter",
        "tools": []
    }
}

def get_config(provider: str = "openrouter") -> Dict[str, Any]:
    """
    Obtiene la configuración para un proveedor específico
    
    Args:
        provider: Proveedor de modelo ("openrouter" o "openai")
    
    Returns:
        Diccionario con la configuración
    """
    if provider not in DEFAULT_CONFIG:
        raise ValueError(f"Proveedor no soportado: {provider}")
    
    config = DEFAULT_CONFIG[provider].copy()
    config["api_key"] = os.getenv(config["env_key"])
    
    if not config["api_key"]:
        raise ValueError(f"Variable de entorno {config['env_key']} no está configurada")
    
    return config

def get_preset_config(preset_name: str) -> Dict[str, Any]:
    """
    Obtiene una configuración predefinida
    
    Args:
        preset_name: Nombre del preset ("agente_clima", "agente_math", "agente_general")
    
    Returns:
        Diccionario con la configuración del preset
    """
    if preset_name not in CUSTOM_CONFIGS:
        raise ValueError(f"Preset no encontrado: {preset_name}")
    
    return CUSTOM_CONFIGS[preset_name].copy()

def create_agent_from_preset(preset_name: str):
    """
    Crea un agente usando una configuración predefinida
    
    Args:
        preset_name: Nombre del preset
    
    Returns:
        Instancia del agente configurado
    """
    from generic_agent import create_agent
    
    preset_config = get_preset_config(preset_name)
    provider_config = get_config(preset_config["model_provider"])
    
    # Combinar configuraciones
    agent_config = {
        "name": preset_config["name"],
        "instructions": preset_config["instructions"],
        "model_provider": preset_config["model_provider"],
        "model_name": provider_config["model_name"],
        "api_key": provider_config["api_key"],
        "base_url": provider_config["base_url"]
    }
    
    # Importar herramientas si están especificadas
    if preset_config.get("tools"):
        from generic_agent import get_weather, calculate, get_time
        tool_map = {
            "get_weather": get_weather,
            "calculate": calculate,
            "get_time": get_time
        }
        agent_config["tools"] = [tool_map[tool] for tool in preset_config["tools"] if tool in tool_map]
    
    return create_agent(**agent_config)

# Función de conveniencia para verificar configuración
def check_configuration():
    """
    Verifica que todas las configuraciones estén correctamente configuradas
    
    Returns:
        Diccionario con el estado de cada proveedor
    """
    status = {}
    
    for provider in DEFAULT_CONFIG:
        try:
            config = get_config(provider)
            status[provider] = {
                "status": "✅ Configurado",
                "model": config["model_name"],
                "base_url": config["base_url"]
            }
        except ValueError as e:
            status[provider] = {
                "status": "❌ Error",
                "error": str(e)
            }
    
    return status

if __name__ == "__main__":
    print("🔧 Verificando configuración del agente...\n")
    
    status = check_configuration()
    for provider, info in status.items():
        print(f"{provider.upper()}: {info['status']}")
        if "error" in info:
            print(f"  Error: {info['error']}")
        else:
            print(f"  Modelo: {info['model']}")
            print(f"  URL: {info['base_url']}")
        print()
    
    print("📋 Presets disponibles:")
    for preset_name in CUSTOM_CONFIGS:
        print(f"  - {preset_name}")
    
    print("\n💡 Para usar un preset:")
    print("  from config_agente import create_agent_from_preset")
    print("  agente = create_agent_from_preset('agente_clima')")
