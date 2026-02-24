package com.discord.bot.Controller;

import org.springframework.web.bind.annotation.RestController;
import com.discord.bot.Repository.GalleryImageRepo;
import com.discord.bot.Repository.GalleryImageVoteRepo;
import com.discord.bot.Service.GalleryImageVoteService;
import com.discord.bot.model.ContestWinner;
import com.discord.bot.model.GalleryImage;
import java.util.List;
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

    private final GalleryImageRepo galleryImageRepo;
    private final GalleryImageVoteService galleryImageVoteService;

    public GalleryImageController(GalleryImageRepo galleryImageRepo, GalleryImageVoteService galleryImageVoteService) {
        this.galleryImageRepo = galleryImageRepo;
        this.galleryImageVoteService = galleryImageVoteService;
    }

    private GalleryImage getImageOrThrow(Long id) {
        return galleryImageRepo.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Image not found with id " + id));
    }

    @GetMapping("/{id}")
    public GalleryImage getImage(@PathVariable Long id) {
        return getImageOrThrow(id);
    }

    @PostMapping("/add")
    public GalleryImage addImage(@RequestParam String url, @RequestParam Long uploaderid) {
        GalleryImage image = new GalleryImage(url, uploaderid);
        return galleryImageRepo.save(image);
    }

    @GetMapping("/{id}/votes")
    public Long getVotes(@PathVariable Long id) {
        return galleryImageVoteService.getVoteCount(getImageOrThrow(id));
    }

    @PostMapping("/{id}/vote")
    public void vote(@PathVariable Long id, @RequestParam Long userID) {
        galleryImageVoteService.addVote(userID, getImageOrThrow(id));
    }

    @DeleteMapping("/{id}")
    public void deleteImage(@PathVariable Long id) {
        galleryImageRepo.delete(getImageOrThrow(id));
    }

    @GetMapping("/all")
    public List<GalleryImage> getAllImages() {
        return galleryImageRepo.findAll();
    }

    @GetMapping("/contest/winner")
    public ContestWinner getContestWinner() {
        GalleryImage winner = galleryImageVoteService.getWinningImage()
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "No contest winner found"));
        ContestWinner contestWinner = new ContestWinner(winner.getUrl(), winner.getuploaderID(),
                galleryImageVoteService.getVoteCount(winner));
        return contestWinner;
    }
}
