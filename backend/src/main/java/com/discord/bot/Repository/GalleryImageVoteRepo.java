package com.discord.bot.Repository;

import com.discord.bot.model.GalleryImage;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import com.discord.bot.model.GalleryImageVote;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.data.domain.Pageable;

public interface GalleryImageVoteRepo extends JpaRepository<GalleryImageVote, Long> {

    Optional<GalleryImageVote> findByUserIdAndGalleryImage(Long userId, GalleryImage image);

    Long countByGalleryImage(GalleryImage image);

    @Query("SELECT v.galleryImage FROM GalleryImageVote v GROUP BY v.galleryImage ORDER BY COUNT(v) DESC")
    List<GalleryImage> findWinningImages(Pageable pageable);

    @Query("SELECT v.galleryImage FROM GalleryImageVote v WHERE v.galleryImage.guildId = :guildId GROUP BY v.galleryImage ORDER BY COUNT(v) DESC")
    List<GalleryImage> findWinningImagesByGuild(@Param("guildId") Long guildId, Pageable pageable);
}
