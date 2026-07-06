---
name: whatsapp-messaging
display_name: "WhatsApp Messaging"
description: "Send and receive WhatsApp messages, manage conversations, and prospect via WhatsApp"
category: messaging
icon: message-square
skill_type: sandbox
catalog_type: platform
requirements: "httpx>=0.25"
resource_requirements:
  - env_var: UNIPILE_DSN
    name: "Unipile API Base URL"
    description: "Unipile REST API endpoint (auto-provided)"
  - env_var: UNIPILE_API_KEY
    name: "Unipile API Key"
    description: "Unipile API authentication key (auto-provided)"
  - env_var: UNIPILE_ACCOUNT_ID
    name: "Unipile Account ID"
    description: "Per-user Unipile account ID (auto-provided by gateway connection)"
tool_schema:
  name: whatsapp_messaging
  description: "Send and receive WhatsApp messages, manage conversations, and start new chats"
  parameters:
    type: object
    properties:
      action:
        type: "string"
        description: "Which operation to perform"
        enum: ['list_chats', 'read_messages', 'send_message', 'start_chat', 'get_chat']
      chat_id:
        type: "string"
        description: "Chat/conversation ID for read_messages, send_message, get_chat"
        default: ""
      text:
        type: "string"
        description: "Message text for send_message and start_chat"
        default: ""
      attendees_ids:
        type: "string"
        description: "Comma-separated user/phone IDs for start_chat"
        default: ""
      limit:
        type: "integer"
        description: "Max results for list_chats and read_messages (default 20)"
        default: 20
    required: [action]
---
# WhatsApp Messaging

Send and receive WhatsApp messages via the Unipile messaging API.

## Conversations
- **list_chats** -- List recent WhatsApp conversations.
- **get_chat** -- Get details of a specific conversation. Provide `chat_id`.

## Messages
- **read_messages** -- Read messages from a conversation. Provide `chat_id` and optional `limit`.
- **send_message** -- Send a message in an existing conversation. Provide `chat_id` and `text`.

## Outreach
- **start_chat** -- Start a new conversation. Provide `attendees_ids` (phone number or user ID) and `text`.
