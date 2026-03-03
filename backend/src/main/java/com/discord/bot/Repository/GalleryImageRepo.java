package com.discord.bot.Repository;

import com.discord.bot.model.GalleryImage;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import com.discord.bot.dto.GalleryImageResponse;
import org.springframework.data.repository.query.Param;
import org.springframework.data.jpa.repository.Query;

public interface GalleryImageRepo extends JpaRepository<GalleryImage, Long> {
    List<GalleryImage> findByGuildid(Long guildid);

    @Query("SELECT new com.discord.bot.dto.GalleryImageResponse(i.id, i.uploaderID, i.guildid, i.title, i.contentType, i.uploadedAt, COUNT(v), i.groupId) "
            +
            "FROM GalleryImage i LEFT JOIN GalleryImageVote v ON v.galleryImage = i " +
            "WHERE i.guildid = :guildid GROUP BY i.id, i.uploaderID, i.guildid, i.title, i.contentType, i.uploadedAt, i.groupId")
    List<GalleryImageResponse> findByGuildidWithVotes(@Param("guildid") Long guildid);

    List<GalleryImage> findByUploaderIDAndGuildid(Long uploaderID, Long guildid);
}
