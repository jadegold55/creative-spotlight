package com.discord.bot.model;

import java.time.LocalDateTime;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;

@Entity
public class GalleryImage {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private long uploaderID;

    private LocalDateTime uploadedAt;

    private String url;

    public GalleryImage() {
    }

    // when imaage is created
    public GalleryImage(String url, long uploaderID) {
        this.url = url;
        this.uploaderID = uploaderID;
        this.uploadedAt = LocalDateTime.now();
    }

    public GalleryImage(String url) {
        this.url = url;
    }

    public long getuploaderID() {
        return uploaderID;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getUrl() {
        return url;
    }

    public void setUploaderID(long uploaderID) {
        this.uploaderID = uploaderID;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public LocalDateTime getUploadedAt() {
        return uploadedAt;
    }
}
