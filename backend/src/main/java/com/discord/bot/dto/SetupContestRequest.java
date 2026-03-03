package com.discord.bot.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record SetupContestRequest(
        @NotNull Long spotlightChannelId,
        @NotNull @Min(0) @Max(6) Integer day,
        @NotNull @Min(0) @Max(23) Integer hour,
        @NotNull @Min(0) @Max(59) Integer minute,
        @NotBlank String timezone,
        @NotNull @Min(1) @Max(30) Integer durationDays) {
}