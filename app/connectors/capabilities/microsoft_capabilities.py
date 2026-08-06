"""Microsoft 365 Shared Capabilities

Defines the capability IDs for Microsoft 365 connectors, ensuring consistency 
across the platform for AI Planner ToolRegistry exposure.
"""

# OneDrive Storage Capabilities
STORAGE_FILES_UPLOAD = "storage.files.upload"
STORAGE_FILES_DOWNLOAD = "storage.files.download"
STORAGE_FILES_DELETE = "storage.files.delete"
STORAGE_FILES_COPY = "storage.files.copy"
STORAGE_FILES_SEARCH = "storage.files.search"
STORAGE_FILES_MOVE = "storage.files.move"
STORAGE_FILES_SHARE = "storage.files.share"
STORAGE_FILES_VERSION_HISTORY = "storage.files.version_history"
STORAGE_FILES_RESTORE_VERSION = "storage.files.restore_version"
STORAGE_FOLDERS_CREATE = "storage.folders.create"
STORAGE_FOLDERS_LIST = "storage.folders.list"
STORAGE_FOLDERS_DELETE = "storage.folders.delete"
STORAGE_SYNC_DELTA = "storage.sync.delta"

# Microsoft To Do Capabilities
PRODUCTIVITY_TASKS_CREATE = "productivity.tasks.create"
PRODUCTIVITY_TASKS_UPDATE = "productivity.tasks.update"
PRODUCTIVITY_TASKS_COMPLETE = "productivity.tasks.complete"
PRODUCTIVITY_TASKS_DELETE = "productivity.tasks.delete"
PRODUCTIVITY_TASKS_LIST = "productivity.tasks.list"
PRODUCTIVITY_TASKS_GET = "productivity.tasks.get"
PRODUCTIVITY_TASKS_SEARCH = "productivity.tasks.search"
PRODUCTIVITY_TASK_LISTS_CREATE = "productivity.task_lists.create"
PRODUCTIVITY_TASK_LISTS_LIST = "productivity.task_lists.list"
PRODUCTIVITY_TASK_LISTS_DELETE = "productivity.task_lists.delete"

# OneNote Capabilities
PRODUCTIVITY_NOTES_CREATE = "productivity.notes.create"
PRODUCTIVITY_NOTES_UPDATE = "productivity.notes.update"
PRODUCTIVITY_NOTES_DELETE = "productivity.notes.delete"
PRODUCTIVITY_NOTES_LIST = "productivity.notes.list"
PRODUCTIVITY_NOTES_GET = "productivity.notes.get"
PRODUCTIVITY_NOTES_SEARCH = "productivity.notes.search"
PRODUCTIVITY_NOTES_COPY = "productivity.notes.copy"
PRODUCTIVITY_NOTES_MOVE = "productivity.notes.move"
PRODUCTIVITY_NOTEBOOKS_CREATE = "productivity.notebooks.create"
PRODUCTIVITY_NOTEBOOKS_LIST = "productivity.notebooks.list"
PRODUCTIVITY_SECTIONS_CREATE = "productivity.sections.create"
PRODUCTIVITY_SECTIONS_LIST = "productivity.sections.list"

# Calendar Expansion Capabilities
CALENDAR_FREE_BUSY_LOOKUP = "calendar.free_busy.lookup"
CALENDAR_EVENTS_CREATE_RECURRING = "calendar.events.create_recurring"
CALENDAR_EVENTS_CANCEL = "calendar.events.cancel"
CALENDAR_EVENTS_INVITE_ATTENDEES = "calendar.events.invite_attendees"

# Contacts Expansion Capabilities
CRM_CONTACTS_FAVORITE = "crm.contacts.favorite"
CRM_CONTACTS_PHOTO = "crm.contacts.photo"
CRM_CONTACT_FOLDERS_LIST = "crm.contact_folders.list"
CRM_CONTACT_FOLDERS_CREATE = "crm.contact_folders.create"

# People API Capabilities
CRM_PEOPLE_SEARCH = "crm.people.search"
CRM_PEOPLE_LIST = "crm.people.list"
CRM_PEOPLE_RECENT = "crm.people.recent"
CRM_PEOPLE_RELEVANT = "crm.people.relevant"
CRM_PEOPLE_ORGANIZATION = "crm.people.organization"

# User Profile Capabilities
USER_PROFILE_GET = "user.profile.get"
USER_PROFILE_PHOTO = "user.profile.photo"
USER_PROFILE_SETTINGS = "user.profile.settings"
