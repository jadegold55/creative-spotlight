package com.discord.bot.dto;

import java.time.LocalDateTime;

public record GalleryImageResponse(Long id, Long uploaderId, Long guildId, String title, String contentType,
        LocalDateTime uploadedAt, Long voteCount, String groupId) {

}
