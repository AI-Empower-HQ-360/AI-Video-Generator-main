# Advanced Automation Configuration
# Configuration file for all automation services

# Video Quality Assessment Configuration
VIDEO_QUALITY_CONFIG = {
    "thresholds": {
        "resolution": {
            "min_width": 720,
            "min_height": 480,
            "recommended_width": 1920,
            "recommended_height": 1080
        },
        "audio": {
            "min_bitrate": 64,
            "recommended_bitrate": 128,
            "sample_rate": 44100
        },
        "video": {
            "min_bitrate": 500,
            "recommended_bitrate": 2000,
            "min_fps": 24,
            "recommended_fps": 30
        },
        "content": {
            "min_duration": 30,
            "max_duration": 3600,
            "silence_threshold": 0.1
        }
    },
    "scoring": {
        "passing_score": 70,
        "excellent_score": 90,
        "good_score": 80
    }
}

# Content Moderation Configuration
CONTENT_MODERATION_CONFIG = {
    "thresholds": {
        "content_appropriateness": 80,
        "spiritual_alignment": 75,
        "quality_score": 70,
        "safety_score": 85,
        "authenticity_score": 70
    },
    "spiritual_keywords": {
        "positive": [
            "meditation", "mindfulness", "peace", "love", "compassion", "wisdom",
            "enlightenment", "spiritual", "divine", "sacred", "prayer", "blessing",
            "dharma", "karma", "moksha", "nirvana", "yoga", "mantra", "chanting",
            "devotion", "surrender", "gratitude", "forgiveness", "healing",
            "consciousness", "awareness", "presence", "tranquility", "serenity"
        ],
        "concerning": [
            "hatred", "violence", "anger", "fear", "discrimination", "prejudice",
            "extremism", "fanaticism", "superiority", "inferiority", "judgment",
            "condemnation", "punishment", "revenge", "manipulation", "exploitation"
        ]
    }
}

# Thumbnail Generation Configuration
THUMBNAIL_GENERATION_CONFIG = {
    "dimensions": {
        "youtube": {"width": 1280, "height": 720},
        "instagram": {"width": 1080, "height": 1080},
        "facebook": {"width": 1200, "height": 630},
        "twitter": {"width": 1200, "height": 675},
        "standard": {"width": 1920, "height": 1080}
    },
    "quality": 85,
    "formats": ["jpg", "png", "webp"],
    "overlay_templates": {
        "meditation": {
            "background_color": "#1a1a2e",
            "text_color": "#eee6ce",
            "accent_color": "#16213e",
            "font_style": "peaceful"
        },
        "chanting": {
            "background_color": "#2c1810",
            "text_color": "#f4e4bc",
            "accent_color": "#8b4513",
            "font_style": "traditional"
        },
        "spiritual_teaching": {
            "background_color": "#0f2027",
            "text_color": "#ffffff",
            "accent_color": "#2c5364",
            "font_style": "elegant"
        },
        "yoga": {
            "background_color": "#1a3b3a",
            "text_color": "#f0f8e8",
            "accent_color": "#4a7c59",
            "font_style": "natural"
        }
    }
}

# Workflow Automation Configuration
WORKFLOW_AUTOMATION_CONFIG = {
    "engine": {
        "max_concurrent_jobs": 5,
        "default_timeout": 1800,  # 30 minutes
        "check_interval": 5,      # seconds
        "retry_delays": [1, 2, 4, 8, 16]  # exponential backoff
    },
    "workflows": {
        "video_processing_complete": {
            "enabled": True,
            "auto_schedule": True,
            "priority": "high",
            "notification_channels": ["email", "slack"]
        },
        "content_moderation_pipeline": {
            "enabled": True,
            "auto_schedule": True,
            "priority": "high",
            "escalation_enabled": True
        },
        "scheduled_quality_assessment": {
            "enabled": True,
            "schedule": "0 2 * * *",  # Daily at 2 AM
            "retention_days": 30
        },
        "performance_optimization": {
            "enabled": True,
            "schedule": "0 4 * * 0",  # Weekly on Sunday at 4 AM
            "retention_days": 90
        }
    }
}

# Disaster Recovery Configuration
DISASTER_RECOVERY_CONFIG = {
    "monitoring": {
        "enabled": True,
        "check_interval": 30,      # seconds
        "health_check_timeout": 10,
        "alert_thresholds": {
            "response_time": 5000,  # ms
            "error_rate": 0.05,     # 5%
            "cpu_usage": 90,        # %
            "memory_usage": 85,     # %
            "disk_usage": 90        # %
        }
    },
    "backup": {
        "enabled": True,
        "default_type": "incremental",
        "retention_policies": {
            "database": {"frequency": "hourly", "retention_days": 30},
            "content_files": {"frequency": "daily", "retention_days": 90},
            "configuration": {"frequency": "daily", "retention_days": 365},
            "user_data": {"frequency": "hourly", "retention_days": 30}
        },
        "encryption": {
            "enabled": True,
            "algorithm": "AES-256",
            "key_rotation_days": 90
        },
        "storage": {
            "primary": "local",
            "secondary": "cloud",
            "cloud_provider": "aws_s3",  # or "azure_blob", "gcp_storage"
            "bucket_name": "spiritual-platform-backups"
        }
    },
    "failover": {
        "enabled": True,
        "automatic_failover": True,
        "failover_threshold": 3,
        "recovery_timeout": 300,
        "standby_servers": [
            "standby-server-1",
            "standby-server-2"
        ]
    }
}

# Performance Testing Configuration
PERFORMANCE_TESTING_CONFIG = {
    "baselines": {
        "response_time": {
            "health_check": 50,
            "ai_guru_chat": 2000,
            "video_quality_check": 5000,
            "content_moderation": 1500,
            "thumbnail_generation": 3000,
            "spiritual_guidance": 1000
        },
        "throughput": {
            "health_check": 1000,
            "ai_guru_chat": 50,
            "video_quality_check": 10,
            "content_moderation": 100,
            "thumbnail_generation": 20,
            "spiritual_guidance": 80
        },
        "error_rate": 0.01,
        "resource_limits": {
            "cpu_usage": 80,
            "memory_usage": 85,
            "disk_io": 90,
            "network_io": 90
        }
    },
    "test_profiles": {
        "light": {"users": 10, "duration": 60},
        "moderate": {"users": 50, "duration": 300},
        "heavy": {"users": 100, "duration": 600},
        "stress": {"users": 200, "duration": 300}
    },
    "monitoring": {
        "enabled": True,
        "check_interval": 300,  # 5 minutes
        "alert_thresholds": {
            "response_time_degradation": 1.5,
            "throughput_degradation": 0.8,
            "error_rate_spike": 0.05,
            "resource_exhaustion": 0.9
        }
    },
    "optimization": {
        "auto_recommendations": True,
        "performance_reports": True,
        "trend_analysis": True,
        "baseline_updates": True
    }
}

# Notification Configuration
NOTIFICATION_CONFIG = {
    "enabled": True,
    "channels": {
        "email": {
            "enabled": True,
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "username": "notifications@spiritual-platform.com",
            "recipients": [
                "admin@spiritual-platform.com",
                "devops@spiritual-platform.com"
            ]
        },
        "slack": {
            "enabled": True,
            "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
            "channel": "#automation-alerts",
            "username": "Automation Bot"
        },
        "discord": {
            "enabled": False,
            "webhook_url": "https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK"
        },
        "teams": {
            "enabled": False,
            "webhook_url": "https://outlook.office.com/webhook/YOUR/TEAMS/WEBHOOK"
        }
    },
    "alert_levels": {
        "critical": {
            "channels": ["email", "slack"],
            "immediate": True,
            "escalation": True
        },
        "warning": {
            "channels": ["slack"],
            "immediate": False,
            "escalation": False
        },
        "info": {
            "channels": ["slack"],
            "immediate": False,
            "escalation": False
        }
    }
}

# API Configuration
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 5001,
    "debug": False,
    "rate_limiting": {
        "enabled": True,
        "default_limit": "100 per hour",
        "endpoints": {
            "/api/automation/video/quality/assess": "10 per minute",
            "/api/automation/video/quality/batch": "5 per minute",
            "/api/automation/performance/test": "5 per hour",
            "/api/automation/disaster-recovery/backup": "10 per hour"
        }
    },
    "authentication": {
        "enabled": True,
        "method": "api_key",  # or "jwt", "oauth"
        "api_key_header": "X-API-Key",
        "required_endpoints": [
            "/api/automation/disaster-recovery/*",
            "/api/automation/system/*"
        ]
    },
    "cors": {
        "enabled": True,
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "headers": ["Content-Type", "Authorization", "X-API-Key"]
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": {
        "console": {
            "enabled": True,
            "level": "INFO"
        },
        "file": {
            "enabled": True,
            "level": "DEBUG",
            "filename": "logs/automation.log",
            "max_bytes": 10485760,  # 10MB
            "backup_count": 5,
            "rotation": True
        },
        "syslog": {
            "enabled": False,
            "level": "WARNING",
            "address": ("localhost", 514),
            "facility": "daemon"
        }
    }
}

# Security Configuration
SECURITY_CONFIG = {
    "encryption": {
        "enabled": True,
        "algorithm": "AES-256-GCM",
        "key_derivation": "PBKDF2",
        "iterations": 100000
    },
    "access_control": {
        "enabled": True,
        "rbac": True,  # Role-based access control
        "roles": {
            "admin": {
                "permissions": ["*"],
                "description": "Full access to all automation features"
            },
            "operator": {
                "permissions": [
                    "video:assess", "content:moderate", "thumbnail:generate",
                    "workflow:view", "workflow:schedule", "performance:view"
                ],
                "description": "Operational access for day-to-day automation tasks"
            },
            "viewer": {
                "permissions": [
                    "video:view", "content:view", "workflow:view", 
                    "performance:view", "system:status"
                ],
                "description": "Read-only access to automation status and reports"
            }
        }
    },
    "audit": {
        "enabled": True,
        "log_requests": True,
        "log_responses": False,
        "sensitive_fields": ["password", "api_key", "token"],
        "retention_days": 90
    }
}

# Environment Configuration
ENVIRONMENT_CONFIG = {
    "development": {
        "debug": True,
        "testing": True,
        "mock_services": True,
        "performance_testing": False
    },
    "staging": {
        "debug": False,
        "testing": True,
        "mock_services": False,
        "performance_testing": True
    },
    "production": {
        "debug": False,
        "testing": False,
        "mock_services": False,
        "performance_testing": True,
        "monitoring": True,
        "alerting": True
    }
}

# Default configuration - combines all sections
DEFAULT_CONFIG = {
    "video_quality": VIDEO_QUALITY_CONFIG,
    "content_moderation": CONTENT_MODERATION_CONFIG,
    "thumbnail_generation": THUMBNAIL_GENERATION_CONFIG,
    "workflow_automation": WORKFLOW_AUTOMATION_CONFIG,
    "disaster_recovery": DISASTER_RECOVERY_CONFIG,
    "performance_testing": PERFORMANCE_TESTING_CONFIG,
    "notifications": NOTIFICATION_CONFIG,
    "api": API_CONFIG,
    "logging": LOGGING_CONFIG,
    "security": SECURITY_CONFIG,
    "environment": ENVIRONMENT_CONFIG
}

# Configuration loading utilities
def load_config(config_file=None, environment="production"):
    """Load configuration from file or use defaults"""
    import json
    import os
    
    config = DEFAULT_CONFIG.copy()
    
    # Load from file if specified
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            file_config = json.load(f)
            config.update(file_config)
    
    # Apply environment-specific settings
    env_config = config.get("environment", {}).get(environment, {})
    for key, value in env_config.items():
        if key in config:
            config[key].update(value if isinstance(value, dict) else {key: value})
    
    # Override with environment variables
    config = _apply_env_overrides(config)
    
    return config

def _apply_env_overrides(config):
    """Apply environment variable overrides"""
    import os
    
    # Database URL
    if os.getenv("DATABASE_URL"):
        config["database_url"] = os.getenv("DATABASE_URL")
    
    # API configuration
    if os.getenv("API_HOST"):
        config["api"]["host"] = os.getenv("API_HOST")
    if os.getenv("API_PORT"):
        config["api"]["port"] = int(os.getenv("API_PORT"))
    
    # Security
    if os.getenv("SECRET_KEY"):
        config["secret_key"] = os.getenv("SECRET_KEY")
    if os.getenv("API_KEY"):
        config["api_key"] = os.getenv("API_KEY")
    
    # Notification webhooks
    if os.getenv("SLACK_WEBHOOK_URL"):
        config["notifications"]["channels"]["slack"]["webhook_url"] = os.getenv("SLACK_WEBHOOK_URL")
    if os.getenv("DISCORD_WEBHOOK_URL"):
        config["notifications"]["channels"]["discord"]["webhook_url"] = os.getenv("DISCORD_WEBHOOK_URL")
    
    # Cloud storage
    if os.getenv("AWS_S3_BUCKET"):
        config["disaster_recovery"]["backup"]["storage"]["bucket_name"] = os.getenv("AWS_S3_BUCKET")
    if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
        config["aws_credentials"] = {
            "access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "region": os.getenv("AWS_REGION", "us-east-1")
        }
    
    return config

def validate_config(config):
    """Validate configuration settings"""
    errors = []
    
    # Validate required settings
    required_settings = [
        "video_quality.thresholds",
        "content_moderation.thresholds",
        "workflow_automation.engine",
        "disaster_recovery.monitoring",
        "performance_testing.baselines"
    ]
    
    for setting in required_settings:
        if not _get_nested_config(config, setting):
            errors.append(f"Missing required setting: {setting}")
    
    # Validate threshold values
    video_thresholds = config.get("video_quality", {}).get("thresholds", {})
    if video_thresholds:
        resolution = video_thresholds.get("resolution", {})
        if resolution.get("min_width", 0) <= 0 or resolution.get("min_height", 0) <= 0:
            errors.append("Invalid video resolution thresholds")
    
    # Validate notification channels
    notifications = config.get("notifications", {})
    if notifications.get("enabled", False):
        channels = notifications.get("channels", {})
        enabled_channels = [name for name, cfg in channels.items() if cfg.get("enabled", False)]
        if not enabled_channels:
            errors.append("No notification channels enabled")
    
    return errors

def _get_nested_config(config, path):
    """Get nested configuration value using dot notation"""
    keys = path.split(".")
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    
    return value

# Export configuration
__all__ = [
    "DEFAULT_CONFIG",
    "VIDEO_QUALITY_CONFIG",
    "CONTENT_MODERATION_CONFIG", 
    "THUMBNAIL_GENERATION_CONFIG",
    "WORKFLOW_AUTOMATION_CONFIG",
    "DISASTER_RECOVERY_CONFIG",
    "PERFORMANCE_TESTING_CONFIG",
    "NOTIFICATION_CONFIG",
    "API_CONFIG",
    "LOGGING_CONFIG",
    "SECURITY_CONFIG",
    "ENVIRONMENT_CONFIG",
    "load_config",
    "validate_config"
]