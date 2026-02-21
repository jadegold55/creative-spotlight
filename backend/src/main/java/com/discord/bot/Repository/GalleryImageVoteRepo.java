package com.discord.bot.Repository;

import com.discord.bot.model.GalleryImage;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import com.discord.bot.model.GalleryImageVote;

public interface GalleryImageVoteRepo extends JpaRepository<GalleryImageVote, Long> {

    public Optional<GalleryImageVote> findByUserIDAndGalleryImage(Long userID, GalleryImage image);

    public Long countByGalleryImage(GalleryImage image);
}
