package com.discord.bot.dto;

import java.time.Instant;

import com.discord.bot.model.GuildSettings;

public record GuildSettingsResponse(
        Long guildId,
        Long spotlightChannelId,
        Long poemChannelId,
        Integer poemHour,
        Integer poemMinute,
        String poemTimezone,
    Instant contestStartAt,
    Instant contestDeadlineAt) {

    public static GuildSettingsResponse from(GuildSettings settings) {
        return new GuildSettingsResponse(
                settings.getGuildId(),
                settings.getSpotlightChannelId(),
                settings.getPoemChannelId(),
                settings.getPoemHour(),
                settings.getPoemMinute(),
                settings.getPoemTimezone(),
        settings.getContestStartAt(),
        settings.getContestDeadlineAt());
    }
}