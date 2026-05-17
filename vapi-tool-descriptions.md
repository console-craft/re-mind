# VAPI Tool Descriptions

## check_reminder_conflicts

- description: Checks whether a proposed reminder overlaps existing scheduled reminders.
- parameters:
```json
{
  "type": "object",
  "properties": {
    "starts_at": {
      "description": "Reminder start time as an ISO 8601 datetime with timezone.",
      "type": "string"
    },
    "duration_minutes": {
      "description": "Reminder duration in minutes. Optional.",
      "type": "integer"
    },
    "exclude_reminder_id": {
      "description": "Existing reminder ID to exclude from conflict checks. Usually omitted.",
      "type": "string"
    }
  },
  "required": [
    "starts_at"
  ]
}
```

## create_reminder
- description: Creates a scheduled reminder after the user has confirmed the reminder details.
- parameters:
```json
{
  "type": "object",
  "properties": {
    "title": {
      "description": "Short reminder title.",
      "type": "string"
    },
    "details": {
      "description": "Optional extra reminder notes.",
      "type": "string"
    },
    "starts_at": {
      "description": "Reminder start time as an ISO 8601 datetime with timezone.",
      "type": "string"
    },
    "time_kind": {
      "description": "Use exact when the reminder has a specific time. Use date_only when the user does not want a specific time.",
      "type": "string",
      "enum": [
        "exact",
        "date_only"
      ]
    },
    "duration_minutes": {
      "description": "Optional reminder duration in minutes.",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "starts_at"
  ]
}
```

## list_reminders

- description: Lists scheduled reminders so the assistant can review existing reminders with the user.
- parameters:
```json
{
  "type": "object",
  "properties": {
    "limit": {
      "description": "Optional maximum number of reminders to return. Must be a positive integer.",
      "type": "integer"
    }
  },
  "required": []
}
get_reminder
- description: Gets the details for one scheduled reminder by ID.
- parameters:
{
  "type": "object",
  "properties": {
    "reminder_id": {
      "description": "ID of the scheduled reminder to retrieve.",
      "type": "string"
    }
  },
  "required": [
    "reminder_id"
  ]
}
```

## get_reminder

- description: Gets the details for one scheduled reminder by ID.
- parameters:
```json
{
  "type": "object",
  "properties": {
    "reminder_id": {
      "description": "ID of the scheduled reminder to retrieve.",
      "type": "string"
    }
  },
  "required": [
    "reminder_id"
  ]
}
```

## update_reminder

- description: Updates an existing scheduled reminder after the user has confirmed the changes.
- parameters:
```json
{
  "type": "object",
  "properties": {
    "reminder_id": {
      "description": "ID of the scheduled reminder to update.",
      "type": "string"
    },
    "title": {
      "description": "Updated short reminder title.",
      "type": "string"
    },
    "details": {
      "description": "Updated optional extra reminder notes.",
      "type": "string"
    },
    "starts_at": {
      "description": "Updated reminder start time as an ISO 8601 datetime with timezone.",
      "type": "string"
    },
    "time_kind": {
      "description": "Use exact when the reminder has a specific time. Use date_only when the user does not want a specific time.",
      "type": "string",
      "enum": [
        "exact",
        "date_only"
      ]
    },
    "duration_minutes": {
      "description": "Updated optional reminder duration in minutes.",
      "type": "integer"
    }
  },
  "required": [
    "reminder_id"
  ]
}
```

## delete_reminder

- description: Deletes/cancels an existing scheduled reminder after the user has confirmed which reminder to remove.
- parameters:
```json
{
  "type": "object",
  "properties": {
    "reminder_id": {
      "description": "ID of the scheduled reminder to delete.",
      "type": "string"
    }
  },
  "required": [
    "reminder_id"
  ]
}
```

