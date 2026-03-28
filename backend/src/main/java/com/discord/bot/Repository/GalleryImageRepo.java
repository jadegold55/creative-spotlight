package com.discord.bot.Repository;

import com.discord.bot.model.GalleryImage;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import com.discord.bot.dto.GalleryImageResponse;
import org.springframework.data.repository.query.Param;
import org.springframework.data.jpa.repository.Query;

public interface GalleryImageRepo extends JpaRepository<GalleryImage, Long> {
    List<GalleryImage> findByGuildId(Long guildId);

    @Query("SELECT new com.discord.bot.dto.GalleryImageResponse(i.id, i.uploaderId, i.guildId, i.title, i.contentType, i.uploadedAt, COUNT(v), i.groupId) "
            +
            "FROM GalleryImage i LEFT JOIN GalleryImageVote v ON v.galleryImage = i " +
            "WHERE i.guildId = :guildId GROUP BY i.id, i.uploaderId, i.guildId, i.title, i.contentType, i.uploadedAt, i.groupId")
    List<GalleryImageResponse> findByGuildIdWithVotes(@Param("guildId") Long guildId);

    List<GalleryImage> findByUploaderIdAndGuildId(Long uploaderId, Long guildId);
}
