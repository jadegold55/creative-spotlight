package com.discord.bot.Repository;

import com.discord.bot.model.GalleryImage;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import com.discord.bot.model.GalleryImageVote;

public interface GalleryImageVoteRepo extends JpaRepository<GalleryImageVote, Long> {
    interface ImageVoteTotal {
        Long getImageId();

        String getImageUrl();

        Long getUploaderId();

        Long getVoteCount();
    }

    public Optional<GalleryImageVote> findByUserIDAndGalleryImage(Long userID, GalleryImage image);

    public Long countByGalleryImage(GalleryImage image);

    @Query("""
            SELECT i.id AS imageId,
                   i.url AS imageUrl,
                   i.uploaderID AS uploaderID,
                   COUNT(v) AS voteCount
            FROM GalleryImage i
            LEFT JOIN GalleryImageVote v ON v.galleryImage = i
            WHERE i.contestId = :contestId
            GROUP BY i.id, i.url, i.uploaderID, i.uploadedAt
            ORDER BY COUNT(v) DESC, i.uploadedAt ASC, i.id ASC
            """)
    List<ImageVoteTotal> findContestVoteTotalsOrderByWinnerRules(@Param("contestId") Long contestId);
}
