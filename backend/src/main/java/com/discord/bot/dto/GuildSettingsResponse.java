package com.discord.bot.dto;

import com.discord.bot.model.GuildSettings;

public record GuildSettingsResponse(
        Long guildId,
        Long spotlightChannelId,
        Long poemChannelId,
        Integer poemHour,
        Integer poemMinute,
        String poemTimezone,
        Integer contestDay,
        Integer contestHour,
        Integer contestMinute,
        String contestTimezone,
        Integer contestDurationDays) {

    public static GuildSettingsResponse from(GuildSettings settings) {
        return new GuildSettingsResponse(
                settings.getGuildId(),
                settings.getSpotlightChannelId(),
                settings.getPoemChannelId(),
                settings.getPoemHour(),
                settings.getPoemMinute(),
                settings.getPoemTimezone(),
                settings.getContestDay(),
                settings.getContestHour(),
                settings.getContestMinute(),
                settings.getContestTimezone(),
                settings.getContestDurationDays());
    }
}