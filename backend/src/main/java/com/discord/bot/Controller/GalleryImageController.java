package com.discord.bot.Controller;

import com.discord.bot.Service.GalleryImageService;
import com.discord.bot.dto.GalleryImageResponse;
import com.discord.bot.model.ContestWinner;
import jakarta.validation.constraints.NotNull;
import java.net.URI;
import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/images")
@Validated
public class GalleryImageController {

    private final GalleryImageService galleryImageService;

    public GalleryImageController(GalleryImageService galleryImageService) {
        this.galleryImageService = galleryImageService;
    }

    @GetMapping("/{id}")
    public GalleryImageResponse getImage(@PathVariable Long id) {
        return galleryImageService.getImage(id);
    }

    @GetMapping("/{id}/file")
    public ResponseEntity<byte[]> getImageFile(@PathVariable Long id) {
        var image = galleryImageService.getImageOrThrow(id);
        return ResponseEntity.ok()
                .header("Content-Type", image.getContentType())
                .body(image.getImageData());
    }

    @GetMapping("/{id}/votes")
    public Long getVotes(@PathVariable Long id) {
        return galleryImageService.getImage(id).voteCount();
    }

    @GetMapping("/all")
    public List<GalleryImageResponse> getAllImages(@RequestParam Long guildId) {
        return galleryImageService.getAllImages(guildId);
    }

    @GetMapping("/contest/winner")
    public ContestWinner getContestWinner(@RequestParam Long guildId) {
        return galleryImageService.getContestWinner(guildId);
    }

    @GetMapping("/user/{uploaderId}")
    public List<GalleryImageResponse> getImagesByUploader(@PathVariable Long uploaderId, @RequestParam Long guildId) {
        return galleryImageService.getImagesByUploader(uploaderId, guildId);
    }

    @PostMapping("/add")
    public ResponseEntity<GalleryImageResponse> addImage(
            @RequestParam("file") MultipartFile file,
            @RequestParam @NotNull Long uploaderId,
            @RequestParam @NotNull Long guildId,
            @RequestParam(required = false) String title) {
        GalleryImageResponse created = galleryImageService.addImage(file, uploaderId, guildId, title);
        return ResponseEntity.created(URI.create("/images/" + created.id())).body(created);
    }

    @PostMapping("/add-multiple")
    public ResponseEntity<List<GalleryImageResponse>> addImages(
            @RequestParam("files") List<MultipartFile> files,
            @RequestParam @NotNull Long uploaderId,
            @RequestParam @NotNull Long guildId,
            @RequestParam(required = false) String title) {
        List<GalleryImageResponse> created = galleryImageService.addImages(files, uploaderId, guildId, title);
        return ResponseEntity.created(URI.create("/images/group/" + created.get(0).groupId())).body(created);
    }

    @PostMapping("/{id}/vote")
    public ResponseEntity<Void> vote(@PathVariable Long id, @RequestParam @NotNull Long userId) {
        galleryImageService.vote(id, userId);
        return ResponseEntity.accepted().build();
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteImage(@PathVariable Long id) {
        galleryImageService.deleteImage(id);
        return ResponseEntity.noContent().build();
    }
}
