package com.discord.bot.Repository;

import com.discord.bot.model.GalleryImage;

import com.discord.bot.model.GalleryImageDTO;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

import com.discord.bot.model.GalleryImageDTO;
import org.springframework.data.repository.query.Param;
import org.springframework.data.jpa.repository.Query;

public interface GalleryImageRepo extends JpaRepository<GalleryImage, Long> {
    List<GalleryImage> findByGuildid(Long guildid);

    @Query("SELECT new com.discord.bot.model.GalleryImageDTO(i.id, i.uploaderID, i.guildid, i.contentType, i.title, COUNT(v)) "
            +
            "FROM GalleryImage i LEFT JOIN GalleryImageVote v ON v.galleryImage = i " +
            "WHERE i.guildid = :guildid GROUP BY i.id, i.uploaderID, i.guildid, i.contentType, i.title")
    List<GalleryImageDTO> findByGuildidWithVotes(@Param("guildid") Long guildid);

    List<GalleryImage> findByUploaderIDAndGuildid(Long uploaderID, Long guildid);
}
