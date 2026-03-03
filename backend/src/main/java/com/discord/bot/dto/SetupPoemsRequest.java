package com.discord.bot.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record SetupPoemsRequest(

        @NotNull Long poemChannelId,
        @NotNull @Min(0) @Max(23) Integer hour,
        @NotNull @Min(0) @Max(59) Integer minute,
        @NotBlank String timezone) {

}
