package com.discord.bot.Controller;

import org.springframework.web.bind.annotation.RestController;
import com.discord.bot.Repository.GalleryImageRepo;
import com.discord.bot.Repository.GalleryImageVoteRepo;
import com.discord.bot.Service.GalleryImageVoteService;
import com.discord.bot.model.GalleryImage;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

@RestController
@RequestMapping("/images")
public class GalleryImageController {

    @Autowired
    private GalleryImageRepo galleryImageRepo;
    @Autowired
    private GalleryImageVoteService galleryImageVoteService;

    @GetMapping("/{id}")
    public GalleryImage getImage(@PathVariable Long id) {
        Optional<GalleryImage> image = galleryImageRepo.findById(id);
        if (image.isPresent()) {
            return image.get();
        } else {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Image not found with id " + id);
        }
    }

    @PostMapping("/add")
    public GalleryImage addImage(@RequestParam String url, @RequestParam Long uploaderid) {
        GalleryImage image = new GalleryImage(url, uploaderid);
        return galleryImageRepo.save(image);
    }

    @GetMapping("/{id}/votes")
    public Long getVotes(@PathVariable Long id) {
        Optional<GalleryImage> image = galleryImageRepo.findById(id);
        if (image.isPresent()) {
            return galleryImageVoteService.getVoteCount(image.get());
        } else {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Image not found with id " + id);
        }
    }

    @PostMapping("/{id}/vote")
    public void vote(@PathVariable Long id, @RequestParam Long userID) {
        Optional<GalleryImage> image = galleryImageRepo.findById(id);
        if (image.isPresent()) {
            galleryImageVoteService.addVote(userID, image.get());
        } else {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Image not found with id " + id);
        }
    }

    @DeleteMapping("/{id}")
    public void deleteImage(@PathVariable Long id) {
        Optional<GalleryImage> image = galleryImageRepo.findById(id);
        if (image.isPresent()) {
            galleryImageRepo.delete(image.get());
        } else {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Image not found with id " + id);
        }
    }

    @GetMapping("/all")
    public List<GalleryImage> getAllImages() {
        return galleryImageRepo.findAll();
    }
}
