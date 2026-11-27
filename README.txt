Lako Battle Spam v1.0.1 - WoW Forever (English client)

Close WoW. Replace the old LakoBattleSpam folder in _forever_/Interface/AddOns/
with the LakoBattleSpam folder from this ZIP. Start WoW and enable the addon.
It works automatically; Universal Chat Filter is not required.

FIX IN 1.0.1
Removed the AddMessage overrides that tainted Blizzard's chat execution and
caused "attempted to iterate a table that cannot be accessed while tainted".
Uses the supported chat event-filter API for system and battleground notices.
Restart WoW after replacing v1.0.0 to clear the already-installed old overrides.

Only numeric notices such as "10 players have joined the battle." are hidden.
Other battleground announcements, including flags and objectives, remain visible.
Existing chat history is not erased. Secret/inaccessible messages pass through.
Chat addons that bypass the supported event filters may still display notices.

/lbspam       Show the version, registration status and session count.
/lbspam test  Check the message matcher without injecting a chat event.

The test checks message matching, not live battleground event delivery.
This hides notices locally and does not repair the underlying game/addon bug.
Disable the addon and /reload to remove its filters.

VALIDATION
Simulated tests cover event filtering, ordinary messages, inaccessible values,
repeated initialization, both supported API names and unchanged chat methods.
Live Forever behavior and interactions with other chat addons need in-game testing.
