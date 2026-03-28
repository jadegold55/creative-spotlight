package com.discord.bot.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Table;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.UniqueConstraint;

@Entity
@Table(name = "GalleryImageVotes", uniqueConstraints = {
        @UniqueConstraint(name = "Unique_Person_and_Unique_Image", columnNames = { "gallery_image_id", "user_id" })
})
public class GalleryImageVote {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @ManyToOne
    @JoinColumn(name = "gallery_image_id")
    private GalleryImage galleryImage;
    @Column(name = "user_id")
    private Long userId;

    public GalleryImageVote() {
    }

    public GalleryImageVote(Long userId, GalleryImage image) {
        this.userId = userId;
        this.galleryImage = image;
    }
}
