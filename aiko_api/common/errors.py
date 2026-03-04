# aiko_api/common/errors.py


class AikoException(Exception):
    """Base exception for aiko_api."""

    pass


class HTTPException(AikoException):
    """Exception that's raised when an HTTP request operation fails."""

    def __init__(self, response, message):
        self.response = response
        self.status = response.status if response else None
        self.message = message
        self.code = None
        self.errors = None

        if isinstance(message, dict):
            self.code = message.get("code")
            self.message = message.get("message", "Unknown error")
            self.errors = message.get("errors")

        if self.status:
            super().__init__(f"{self.status} {self.message}")
        else:
            super().__init__(self.message)


class Forbidden(HTTPException):
    """Exception that's raised for a 403 status code."""

    pass


class NotFound(HTTPException):
    """Exception that's raised for a 404 status code."""

    pass


class DiscordServerError(HTTPException):
    """Exception that's raised for a 500 range status code."""

    pass


class LoginFailure(AikoException):
    """Exception that's raised when the token is invalid."""

    pass


# Discord API specific error types
class RateLimited(HTTPException):
    """Exception that's raised when rate limited."""

    def __init__(self, response, message):
        super().__init__(response, message)
        self.retry_after = None
        if isinstance(message, dict):
            self.retry_after = float(message.get("retry_after", 1))


class InvalidData(AikoException):
    """Exception that's raised when invalid data is provided."""

    pass


class InvalidArgument(AikoException):
    """Exception that's raised when an invalid argument is provided."""

    pass


class ClientException(AikoException):
    """Exception that's raised when a client operation fails."""

    pass


class ConnectionClosed(AikoException):
    """Exception that's raised when the connection is closed."""

    pass


class GatewayNotFound(AikoException):
    """Exception that's raised when the gateway is not found."""

    pass


class PrivilegedIntentsRequired(AikoException):
    """Exception that's raised when privileged intents are required but not enabled."""

    pass


# Specific Discord API error codes
class DiscordAPIError(HTTPException):
    """Base class for Discord API specific errors."""

    def __init__(self, response, message, code=None):
        super().__init__(response, message)
        self.code = code


class UnknownAccount(DiscordAPIError):
    """Unknown account."""

    CODE = 10001


class UnknownApplication(DiscordAPIError):
    """Unknown application."""

    CODE = 10002


class UnknownChannel(DiscordAPIError):
    """Unknown channel."""

    CODE = 10003


class UnknownGuild(DiscordAPIError):
    """Unknown guild."""

    CODE = 10004


class UnknownIntegration(DiscordAPIError):
    """Unknown integration."""

    CODE = 10005


class UnknownInvite(DiscordAPIError):
    """Unknown invite."""

    CODE = 10006


class UnknownMember(DiscordAPIError):
    """Unknown member."""

    CODE = 10007


class UnknownMessage(DiscordAPIError):
    """Unknown message."""

    CODE = 10008


class UnknownPermissionOverwrite(DiscordAPIError):
    """Unknown permission overwrite."""

    CODE = 10009


class UnknownProvider(DiscordAPIError):
    """Unknown provider."""

    CODE = 10010


class UnknownRole(DiscordAPIError):
    """Unknown role."""

    CODE = 10011


class UnknownToken(DiscordAPIError):
    """Unknown token."""

    CODE = 10012


class UnknownUser(DiscordAPIError):
    """Unknown user."""

    CODE = 10013


class UnknownEmoji(DiscordAPIError):
    """Unknown emoji."""

    CODE = 10014


class UnknownWebhook(DiscordAPIError):
    """Unknown webhook."""

    CODE = 10015


class BotsCannotUseEndpoint(DiscordAPIError):
    """Bots cannot use this endpoint."""

    CODE = 20001


class OnlyBotsCanUseEndpoint(DiscordAPIError):
    """Only bots can use this endpoint."""

    CODE = 20002


class MessageCannotBeEdited(DiscordAPIError):
    """Message cannot be edited."""

    CODE = 22000


class TooManyGuilds(DiscordAPIError):
    """Too many guilds."""

    CODE = 30001


class TooManyFriends(DiscordAPIError):
    """Too many friends."""

    CODE = 30002


class TooManyPins(DiscordAPIError):
    """Too many pins."""

    CODE = 30003


class TooManyRecipients(DiscordAPIError):
    """Too many recipients."""

    CODE = 30004


class TooManyGuildRoles(DiscordAPIError):
    """Too many guild roles."""

    CODE = 30005


class TooManyWebhooks(DiscordAPIError):
    """Too many webhooks."""

    CODE = 30007


class TooManyEmojis(DiscordAPIError):
    """Too many emojis."""

    CODE = 30008


class TooManyReactions(DiscordAPIError):
    """Too many reactions."""

    CODE = 30010


class Unauthorized(DiscordAPIError):
    """Unauthorized."""

    CODE = 40001


class AccountNeedsVerification(DiscordAPIError):
    """Account needs verification."""

    CODE = 40002


class RequestEntityTooLarge(DiscordAPIError):
    """Request entity too large."""

    CODE = 40005


class FeatureTemporarilyDisabled(DiscordAPIError):
    """Feature temporarily disabled."""

    CODE = 40006


class UserBanned(DiscordAPIError):
    """User banned."""

    CODE = 40007


class AlreadyCrossposted(DiscordAPIError):
    """Already crossposted."""

    CODE = 40008


class MissingAccess(DiscordAPIError):
    """Missing access."""

    CODE = 50001


class InvalidAccountType(DiscordAPIError):
    """Invalid account type."""

    CODE = 50002


class CannotExecuteOnDM(DiscordAPIError):
    """Cannot execute on DM."""

    CODE = 50003


class GuildWidgetDisabled(DiscordAPIError):
    """Guild widget disabled."""

    CODE = 50004


class CannotEditMessageByOther(DiscordAPIError):
    """Cannot edit message by other."""

    CODE = 50005


class CannotSendEmptyMessage(DiscordAPIError):
    """Cannot send empty message."""

    CODE = 50006


class CannotSendMessageToUser(DiscordAPIError):
    """Cannot send message to user."""

    CODE = 50007


class CannotSendMessagesInVoiceChannel(DiscordAPIError):
    """Cannot send messages in voice channel."""

    CODE = 50008


class ChannelVerificationTooHigh(DiscordAPIError):
    """Channel verification too high."""

    CODE = 50009


class OAuth2ApplicationDoesNotHaveBot(DiscordAPIError):
    """OAuth2 application does not have bot."""

    CODE = 50010


class OAuth2ApplicationLimitReached(DiscordAPIError):
    """OAuth2 application limit reached."""

    CODE = 50011


class InvalidOAuth2State(DiscordAPIError):
    """Invalid OAuth2 state."""

    CODE = 50012


class MissingPermissions(DiscordAPIError):
    """Missing permissions."""

    CODE = 50013


class InvalidAuthenticationToken(DiscordAPIError):
    """Invalid authentication token."""

    CODE = 50014


class NoteTooLong(DiscordAPIError):
    """Note too long."""

    CODE = 50015


class TooFewOrTooManyMessagesToDelete(DiscordAPIError):
    """Too few or too many messages to delete."""

    CODE = 50016


class InvalidMFALevel(DiscordAPIError):
    """Invalid MFA level."""

    CODE = 50017


class InvalidMessageID(DiscordAPIError):
    """Invalid message ID."""

    CODE = 50019


class InvalidEmoji(DiscordAPIError):
    """Invalid emoji."""

    CODE = 50014


# Error code mapping
ERROR_CODE_MAP = {
    10001: UnknownAccount,
    10002: UnknownApplication,
    10003: UnknownChannel,
    10004: UnknownGuild,
    10005: UnknownIntegration,
    10006: UnknownInvite,
    10007: UnknownMember,
    10008: UnknownMessage,
    10009: UnknownPermissionOverwrite,
    10010: UnknownProvider,
    10011: UnknownRole,
    10012: UnknownToken,
    10013: UnknownUser,
    10014: UnknownEmoji,
    10015: UnknownWebhook,
    20001: BotsCannotUseEndpoint,
    20002: OnlyBotsCanUseEndpoint,
    22000: MessageCannotBeEdited,
    30001: TooManyGuilds,
    30002: TooManyFriends,
    30003: TooManyPins,
    30004: TooManyRecipients,
    30005: TooManyGuildRoles,
    30007: TooManyWebhooks,
    30008: TooManyEmojis,
    30010: TooManyReactions,
    40001: Unauthorized,
    40002: AccountNeedsVerification,
    40005: RequestEntityTooLarge,
    40006: FeatureTemporarilyDisabled,
    40007: UserBanned,
    40008: AlreadyCrossposted,
    50001: MissingAccess,
    50002: InvalidAccountType,
    50003: CannotExecuteOnDM,
    50004: GuildWidgetDisabled,
    50005: CannotEditMessageByOther,
    50006: CannotSendEmptyMessage,
    50007: CannotSendMessageToUser,
    50008: CannotSendMessagesInVoiceChannel,
    50009: ChannelVerificationTooHigh,
    50010: OAuth2ApplicationDoesNotHaveBot,
    50011: OAuth2ApplicationLimitReached,
    50012: InvalidOAuth2State,
    50013: MissingPermissions,
    50014: InvalidAuthenticationToken,
    50015: NoteTooLong,
    50016: TooFewOrTooManyMessagesToDelete,
    50017: InvalidMFALevel,
    50019: InvalidMessageID,
}


def get_discord_error(response, message):
    """Get the appropriate Discord API error based on the error code."""
    if isinstance(message, dict) and "code" in message:
        code = message["code"]
        error_class = ERROR_CODE_MAP.get(code, DiscordAPIError)
        return error_class(response, message, code)
    return DiscordAPIError(response, message)
