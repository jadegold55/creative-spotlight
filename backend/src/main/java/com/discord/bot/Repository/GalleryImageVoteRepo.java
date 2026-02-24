package com.discord.bot.Repository;

import com.discord.bot.model.GalleryImage;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import com.discord.bot.model.GalleryImageVote;
import org.springframework.data.jpa.repository.Query;

public interface GalleryImageVoteRepo extends JpaRepository<GalleryImageVote, Long> {

    public Optional<GalleryImageVote> findByUserIDAndGalleryImage(Long userID, GalleryImage image);

    public Long countByGalleryImage(GalleryImage image);

    @Query("SELECT v.galleryImage FROM GalleryImageVote v GROUP BY v.galleryImage ORDER BY COUNT(v) DESC LIMIT 1")
    Optional<GalleryImage> findWinningImage();
}
