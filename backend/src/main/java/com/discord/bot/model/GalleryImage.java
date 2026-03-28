package com.discord.bot.model;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import jakarta.persistence.CascadeType;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Column;
import jakarta.persistence.Lob;

import com.fasterxml.jackson.annotation.JsonIgnore;

@Entity
public class GalleryImage {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name = "uploader_id")
    private Long uploaderId;
    @Column(name = "guild_id")
    private Long guildId;
    private LocalDateTime uploadedAt;
    private String contentType;
    private String title;
    @Column(name = "group_id")
    private String groupId;
    @JsonIgnore
    @Column(columnDefinition = "bytea")
    private byte[] imageData;
    @OneToMany(mappedBy = "galleryImage", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<GalleryImageVote> votes;

    public GalleryImage() {
    }

    public GalleryImage(String contentType, byte[] imageData, Long uploaderId, Long guildId) {
        this.contentType = contentType;
        this.imageData = imageData;
        this.uploaderId = uploaderId;
        this.guildId = guildId;
        this.groupId = UUID.randomUUID().toString();
        this.uploadedAt = LocalDateTime.now();
    }

    public GalleryImage(String contentType, byte[] imageData, Long uploaderId, Long guildId, String groupId) {
        this.contentType = contentType;
        this.imageData = imageData;
        this.uploaderId = uploaderId;
        this.guildId = guildId;
        this.groupId = groupId;
        this.uploadedAt = LocalDateTime.now();
    }

    public Long getUploaderId() {
        return uploaderId;
    }

    public void setUploaderId(Long uploaderId) {
        this.uploaderId = uploaderId;
    }

    public Long getGuildId() {
        return guildId;
    }

    public void setGuildId(Long guildId) {
        this.guildId = guildId;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getContentType() {
        return contentType;
    }

    public void setContentType(String contentType) {
        this.contentType = contentType;
    }

    public byte[] getImageData() {
        return imageData;
    }

    public void setImageData(byte[] imageData) {
        this.imageData = imageData;
    }

    public LocalDateTime getUploadedAt() {
        return uploadedAt;
    }

    public void setUploadedAt(LocalDateTime uploadedAt) {
        this.uploadedAt = uploadedAt;
    }

    public String getGroupId() {
        return groupId;
    }

    public void setGroupId(String groupId) {
        this.groupId = groupId;
    }
}
