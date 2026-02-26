package com.discord.bot.Repository;

import com.discord.bot.model.GalleryImage;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

public interface GalleryImageRepo extends JpaRepository<GalleryImage, Long> {
    List<GalleryImage> findByGuildid(Long guildid);
}
