package com.discord.bot.Repository;

import com.discord.bot.model.GalleryImage;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;

public interface GalleryImageRepo extends JpaRepository<GalleryImage, Long> {
    List<GalleryImage> findByContestId(Long contestId);

    Optional<GalleryImage> findFirstByContestIdOrderByContestDeadlineAscIdAsc(Long contestId);
}
