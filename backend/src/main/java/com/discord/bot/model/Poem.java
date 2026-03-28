package com.discord.bot.model;

import java.time.LocalDateTime;
import jakarta.persistence.Column;
import jakarta.persistence.Enumerated;
import jakarta.persistence.EnumType;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;

@Entity
public class Poem {

    public enum PoemType {
        DAILY,
        USER_UPLOAD
    }

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name = "uploader_id")
    private Long uploaderId;
    private LocalDateTime postedAt;
    private String content;
    private String title;
    private String author;
    @Enumerated(EnumType.STRING)
    private PoemType poemType;

    public Poem() {
    }

    public Poem(Long uploaderId, LocalDateTime postedAt, String content, String title, String author) {
        this.uploaderId = uploaderId;
        this.postedAt = LocalDateTime.now();
        this.content = content;
        this.title = title;
        this.author = author;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getUploaderId() {
        return uploaderId;
    }

    public void setUploaderId(Long uploaderId) {
        this.uploaderId = uploaderId;
    }

    public LocalDateTime getPostedAt() {
        return postedAt;
    }

    public void setPostedAt(LocalDateTime postedAt) {
        this.postedAt = postedAt;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getAuthor() {
        return author;
    }

    public void setAuthor(String author) {
        this.author = author;
    }
}
