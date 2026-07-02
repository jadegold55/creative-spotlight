package com.discord.bot.Service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.discord.bot.Exceptions.InvalidVote;
import com.discord.bot.Repository.GalleryImageVoteRepo;
import com.discord.bot.model.GalleryImage;
import com.discord.bot.model.GalleryImageVote;

@ExtendWith(MockitoExtension.class)
class GalleryImageVoteServiceTest {
    @Mock
    private GalleryImageVoteRepo galleryImageVoteRepo;

    private GalleryImageVoteService galleryImageVoteService;

    @BeforeEach
    void setUp() {
        galleryImageVoteService = new GalleryImageVoteService(galleryImageVoteRepo);
    }

    @Test
    void addVoteSavesNewVoteWhenUserHasNotVotedForImage() {
        GalleryImage image = new GalleryImage("image/png", new byte[] { 1 }, 99L, 42L);
        when(galleryImageVoteRepo.findByUserIdAndGalleryImage(123L, image)).thenReturn(Optional.empty());

        galleryImageVoteService.addVote(123L, image);

        verify(galleryImageVoteRepo).save(any(GalleryImageVote.class));
    }

    @Test
    void addVoteRejectsDuplicateVoteForSameImage() {
        GalleryImage image = new GalleryImage("image/png", new byte[] { 1 }, 99L, 42L);
        when(galleryImageVoteRepo.findByUserIdAndGalleryImage(123L, image))
                .thenReturn(Optional.of(new GalleryImageVote(123L, image)));

        assertThrows(InvalidVote.class, () -> galleryImageVoteService.addVote(123L, image));

        verify(galleryImageVoteRepo, never()).save(any());
    }

    @Test
    void getVoteCountDelegatesToRepository() {
        GalleryImage image = new GalleryImage("image/png", new byte[] { 1 }, 99L, 42L);
        when(galleryImageVoteRepo.countByGalleryImage(image)).thenReturn(7L);

        Long count = galleryImageVoteService.getVoteCount(image);

        assertEquals(7L, count);
    }
}
