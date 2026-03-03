package com.discord.bot.dto;

public record SetupChannelsRequest(
        Long poemChannelId,
        Long spotlightChannelId) {
}