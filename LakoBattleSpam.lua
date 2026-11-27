-- Narrow filter for the English numeric battleground join notice.
-- v1.0.1: supported event filters only; never replace chat-frame methods.
local blocked, filtersRegistered = 0, false

local function IsJoinNotice(message)
    if issecretvalue and issecretvalue(message) then return false end
    if type(message) ~= "string" then return false end
    if not message:find("players have joined the battle", 1, true) then return false end
    local text = message:gsub("|c%x%x%x%x%x%x%x%x", ""):gsub("|r", "")
    text = text:gsub("^%s*%[%d[%d:%.%sAPMapm]*%]%s*", "")
    text = text:gsub("^%s*%d%d?:%d%d:?%d*%s*", "")
    return text:match("^%s*%d+ players have joined the battle%.%s*$") ~= nil
end

local function ShouldHide(message)
    -- Leave inaccessible messages alone instead of interrupting chat.
    local ok, result = pcall(IsJoinNotice, message)
    return ok and result
end

local function Filter(_, _, message)
    if ShouldHide(message) then
        blocked = blocked + 1
        return true
    end
    return false
end

local function Install()
    if not filtersRegistered then
        local register = ChatFrameUtil and ChatFrameUtil.AddMessageEventFilter
            or ChatFrame_AddMessageEventFilter
        if type(register) == "function" then
            for _, event in ipairs({ "CHAT_MSG_SYSTEM", "CHAT_MSG_BG_SYSTEM_NEUTRAL",
                "CHAT_MSG_BG_SYSTEM_ALLIANCE", "CHAT_MSG_BG_SYSTEM_HORDE" }) do
                register(event, Filter)
            end
            filtersRegistered = true
        end
    end
end

local function Print(text)
    if DEFAULT_CHAT_FRAME then DEFAULT_CHAT_FRAME:AddMessage("Lako Battle Spam: " .. text) end
end

SLASH_LAKOBATTLESPAM1 = "/lbspam"
SlashCmdList.LAKOBATTLESPAM = function(input)
    if input == "test" then
        local passed = ShouldHide("10 players have joined the battle.")
            and not ShouldHide("The battle has begun!")
        Print(passed and "message matcher check passed (not a live battleground test)."
            or "message matcher check failed.")
    else
        Install()
        Print("v1.0.1 " .. (filtersRegistered and "active" or "waiting for chat filter API")
            .. "; " .. blocked .. " notices filtered this session.")
    end
end

local loader = CreateFrame("Frame")
loader:RegisterEvent("PLAYER_LOGIN")
loader:RegisterEvent("PLAYER_ENTERING_WORLD")
loader:SetScript("OnEvent", function()
    Install()
end)
