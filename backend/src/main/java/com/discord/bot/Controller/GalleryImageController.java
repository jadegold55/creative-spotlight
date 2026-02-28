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
import org.springframework.web.multipart.MultipartFile;
import org.springframework.http.ResponseEntity;
import java.io.IOException;

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

    // @GetMapping("random")
    @GetMapping("/{id}/file")
    public ResponseEntity<byte[]> getImageFile(@PathVariable Long id) {
        GalleryImage image = getImageOrThrow(id);
        return ResponseEntity.ok()
                .header("Content-Type", image.getContentType())
                .body(image.getImageData());
    }

    @PostMapping("/add")
    public GalleryImage addImage(@RequestParam("file") MultipartFile file, @RequestParam Long uploaderid,
            @RequestParam Long guildid) {
        try {
            GalleryImage image = new GalleryImage(file.getContentType(), file.getBytes(), uploaderid, guildid);
            return galleryImageRepo.save(image);
        } catch (IOException e) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Failed to read image file", e);
        }
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
    public List<GalleryImage> getAllImages(@RequestParam(required = false) Long guildid) {
        if (guildid != null) {
            return galleryImageRepo.findByGuildid(guildid);
        }
        return galleryImageRepo.findAll();
    }

    @GetMapping("/contest/winner")
    public ContestWinner getContestWinner(@RequestParam Long guildid) {
        GalleryImage winner = galleryImageVoteService.getWinningImage(guildid)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "No contest winner found"));
        return new ContestWinner(winner.getId(), winner.getuploaderID(),
                galleryImageVoteService.getVoteCount(winner));
    }
}
