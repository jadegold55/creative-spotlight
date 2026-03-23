package com.discord.bot.dto;

import java.time.Instant;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record ContestSignupsResponse(Long id, @NotNull Long userId, @NotNull Long guildId,
        @NotBlank String username, @NotNull Boolean isVerified, @NotNull Instant signupDeadlineAt) {

}
