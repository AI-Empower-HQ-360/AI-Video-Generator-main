"""
Slack, Teams, and Discord bot integrations for video notifications.
Provides messaging capabilities across popular team communication platforms.
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
try:
    from flask import current_app
except ImportError:
    # Mock current_app when Flask is not available
    class MockApp:
        class Logger:
            def error(self, msg): print(f"ERROR: {msg}")
            def info(self, msg): print(f"INFO: {msg}")
        logger = Logger()
    current_app = MockApp()


class SlackBot:
    """Slack bot for video notifications and commands."""
    
    def __init__(self, bot_token: Optional[str] = None, webhook_url: Optional[str] = None):
        self.bot_token = bot_token
        self.webhook_url = webhook_url
        self.base_url = "https://slack.com/api"
    
    def send_video_notification(self, channel: str, video_data: Dict[str, Any]) -> bool:
        """Send video completion notification to Slack channel."""
        message_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🎥 *New Video Generated!*\n*{video_data.get('title', 'Untitled Video')}*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Duration:*\n{video_data.get('duration', 'N/A')} seconds"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Guru:*\n{video_data.get('guru', 'Unknown')}"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Watch Video"
                        },
                        "url": video_data.get('url', '#'),
                        "style": "primary"
                    }
                ]
            }
        ]
        
        return self._send_message(channel, blocks=message_blocks)
    
    def _send_message(self, channel: str, text: str = "", blocks: List[Dict] = None) -> bool:
        """Send message to Slack channel."""
        try:
            if self.webhook_url:
                # Use incoming webhook
                payload = {
                    "channel": channel,
                    "text": text,
                    "blocks": blocks or []
                }
                response = requests.post(self.webhook_url, json=payload)
                return response.status_code == 200
            
            elif self.bot_token:
                # Use bot token
                headers = {
                    "Authorization": f"Bearer {self.bot_token}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "channel": channel,
                    "text": text,
                    "blocks": blocks or []
                }
                
                response = requests.post(
                    f"{self.base_url}/chat.postMessage",
                    headers=headers,
                    json=payload
                )
                
                return response.status_code == 200
        
        except Exception as e:
            current_app.logger.error(f"Slack message failed: {str(e)}")
            return False


class TeamsBot:
    """Microsoft Teams bot for video notifications."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url
    
    def send_video_notification(self, video_data: Dict[str, Any]) -> bool:
        """Send video notification to Teams channel."""
        if not self.webhook_url:
            return False
        
        card = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": "New Video Generated",
            "sections": [
                {
                    "activityTitle": "🎥 New Video Generated!",
                    "activitySubtitle": video_data.get('title', 'Untitled Video'),
                    "facts": [
                        {
                            "name": "Duration",
                            "value": f"{video_data.get('duration', 'N/A')} seconds"
                        },
                        {
                            "name": "Guru",
                            "value": video_data.get('guru', 'Unknown')
                        },
                        {
                            "name": "Created",
                            "value": video_data.get('created_at', datetime.utcnow().isoformat())
                        }
                    ],
                    "markdown": True
                }
            ],
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "Watch Video",
                    "targets": [
                        {
                            "os": "default",
                            "uri": video_data.get('url', '#')
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(self.webhook_url, json=card)
            return response.status_code == 200
        except Exception as e:
            current_app.logger.error(f"Teams message failed: {str(e)}")
            return False


class DiscordBot:
    """Discord bot for video notifications and community sharing."""
    
    def __init__(self, webhook_url: Optional[str] = None, bot_token: Optional[str] = None):
        self.webhook_url = webhook_url
        self.bot_token = bot_token
        self.base_url = "https://discord.com/api"
    
    def send_video_notification(self, video_data: Dict[str, Any]) -> bool:
        """Send video notification to Discord channel."""
        if not self.webhook_url:
            return False
        
        embed = {
            "title": "🎥 New Video Generated!",
            "description": video_data.get('title', 'Untitled Video'),
            "color": 5814783,  # Blue color
            "fields": [
                {
                    "name": "Duration",
                    "value": f"{video_data.get('duration', 'N/A')} seconds",
                    "inline": True
                },
                {
                    "name": "Guru",
                    "value": video_data.get('guru', 'Unknown'),
                    "inline": True
                }
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "AI Video Generator"
            }
        }
        
        if video_data.get('thumbnail'):
            embed["thumbnail"] = {"url": video_data['thumbnail']}
        
        payload = {
            "embeds": [embed]
        }
        
        if video_data.get('url'):
            payload["content"] = f"Watch here: {video_data['url']}"
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            return response.status_code in [200, 204]
        except Exception as e:
            current_app.logger.error(f"Discord message failed: {str(e)}")
            return False


class NotificationManager:
    """Manages notifications across all communication platforms."""
    
    def __init__(self):
        self.slack_bot = SlackBot()
        self.teams_bot = TeamsBot()
        self.discord_bot = DiscordBot()
        self.enabled_platforms = []
    
    def configure_slack(self, bot_token: str = None, webhook_url: str = None):
        """Configure Slack integration."""
        self.slack_bot = SlackBot(bot_token, webhook_url)
        if 'slack' not in self.enabled_platforms:
            self.enabled_platforms.append('slack')
    
    def configure_teams(self, webhook_url: str):
        """Configure Teams integration."""
        self.teams_bot = TeamsBot(webhook_url)
        if 'teams' not in self.enabled_platforms:
            self.enabled_platforms.append('teams')
    
    def configure_discord(self, webhook_url: str = None, bot_token: str = None):
        """Configure Discord integration."""
        self.discord_bot = DiscordBot(webhook_url, bot_token)
        if 'discord' not in self.enabled_platforms:
            self.enabled_platforms.append('discord')
    
    def notify_video_generated(self, video_data: Dict[str, Any], platforms: List[str] = None):
        """Send video notification to specified platforms."""
        target_platforms = platforms or self.enabled_platforms
        
        results = {}
        
        if 'slack' in target_platforms and 'slack' in self.enabled_platforms:
            results['slack'] = self.slack_bot.send_video_notification(
                channel="#videos", 
                video_data=video_data
            )
        
        if 'teams' in target_platforms and 'teams' in self.enabled_platforms:
            results['teams'] = self.teams_bot.send_video_notification(video_data)
        
        if 'discord' in target_platforms and 'discord' in self.enabled_platforms:
            results['discord'] = self.discord_bot.send_video_notification(video_data)
        
        return results


# Global notification manager instance
notification_manager = NotificationManager()