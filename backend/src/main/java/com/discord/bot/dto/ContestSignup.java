package com.discord.bot.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record ContestSignup(Long id, @NotNull Long userId, @NotNull Long contestId, @NotNull Long guildId,
        @NotBlank String username, @NotNull Boolean isVerified) {

}
