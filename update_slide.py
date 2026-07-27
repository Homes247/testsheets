import re

with open("frontend/src/app/pages/slide-editor/slide-editor.component.ts", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add video upload to Insert Menu
insert_old = """<div class="dd-item" (click)="triggerImageInsert()"><span class="dd-text">Image</span></div>"""
insert_new = """<div class="dd-item" (click)="triggerImageInsert()"><span class="dd-text">Image</span></div>
<div class="dd-item" (click)="triggerVideoInsert()"><span class="dd-text">Video</span></div>"""
content = content.replace(insert_old, insert_new)

# 2. Add Video Modal HTML
img_modal_old = """<!-- Image Modal -->
      <div class="modal-overlay" *ngIf="imageModalOpen" (click)="imageModalOpen = false">"""
vid_modal_new = """<!-- Video Modal -->
      <div class="modal-overlay" *ngIf="videoModalOpen" (click)="videoModalOpen = false">
        <div class="modal" style="width: 400px; padding: 24px;" (click)="$event.stopPropagation()">
          <h3 style="margin-top:0;">Insert Video</h3>
          <p style="color:#5f6368;font-size:14px;margin-bottom:16px;">Option 1: Upload a file</p>
          
          <div class="upload-area" style="border:2px dashed #dadce0; border-radius:8px; padding:32px; text-align:center; margin-bottom:16px; background:#f8f9fa;">
            <input type="file" #vidInput accept="video/*" style="display:none" (change)="uploadVideo($event)">
            <button class="btn outline" style="width:100%" (click)="vidInput.click()">Select File</button>
          </div>
          
          <div style="text-align:center;color:#9aa0a6;margin-bottom:16px;font-size:12px;">— OR —</div>
          
          <p style="color:#5f6368;font-size:14px;margin-bottom:8px;">Option 2: By URL</p>
          <input type="text" [(ngModel)]="videoUrl" placeholder="https://" style="width:100%;padding:8px;margin-bottom:16px;box-sizing:border-box;border:1px solid #ccc;border-radius:4px;" />
          <div style="display:flex;justify-content:flex-end;gap:8px;">
            <button class="btn outline" (click)="videoModalOpen = false">Cancel</button>
            <button class="btn blue-btn" (click)="insertVideo()">Insert URL</button>
          </div>
        </div>
      </div>
      
      <!-- Image Modal -->
      <div class="modal-overlay" *ngIf="imageModalOpen" (click)="imageModalOpen = false">"""
content = content.replace(img_modal_old, vid_modal_new)

# 3. Add Video state and methods
vid_methods_new = """
  // -- Video / Reaction Methods --
  videoModalOpen = false;
  videoUrl = '';

  triggerVideoInsert() {
    this.closeMenus();
    this.videoModalOpen = true;
    this.videoUrl = '';
  }

  insertVideoHtml(url: string) {
    if (!this.slideBodyRef || !this.activePage) return;
    this.slideBodyRef.nativeElement.focus();
    
    // Instead of execCommand, let's append a resizable video block directly
    // to allow free drag/resize just like images.
    const html = `<video src="${url}" controls style="width:300px; height:auto; position:absolute; left:50px; top:50px;"></video>`;
    this.slideBodyRef.nativeElement.innerHTML += html;
    
    this.activePage.body = this.slideBodyRef.nativeElement.innerHTML;
    this.onChanged();
  }

  insertVideo() {
    if (this.videoUrl) {
      this.insertVideoHtml(this.videoUrl);
    }
    this.videoModalOpen = false;
  }

  uploadVideo(e: any) {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (re) => {
        const dataUrl = re.target?.result as string;
        this.insertVideoHtml(dataUrl);
      };
      reader.readAsDataURL(file);
    }
    e.target.value = '';
    this.videoModalOpen = false;
  }

  downloadSelectedSlideMedia() {
    if (!this.activeImg) return;
    const src = this.activeImg.getAttribute('src');
    if (!src) return;
    const a = document.createElement('a');
    a.href = src;
    a.download = 'slide_media';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  // Reactions
  slideReactionEmojis = ['👍', '❤️', '😂', '😲', '😢', '😡'];
  showSlideMediaReactions = false;
  showSlideEmojiPickerModal = false;

  toggleSlideMediaReactions(event: Event) {
    event.stopPropagation();
    this.showSlideMediaReactions = !this.showSlideMediaReactions;
    this.showSlideEmojiPickerModal = false;
  }

  addSlideMediaReaction(emoji: string) {
    if (!this.activeImg) return;
    // We add a badge inside the slide body, absolutely positioned relative to activeImg
    // But since activeImg is absolutely positioned, we can just append a badge to slideBody
    // at activeImg's location, or better wrap activeImg. But in slide editor, items are flat.
    // Let's just create a div next to it for now.
    let badge = document.createElement('div');
    badge.className = 'slide-reaction-badge';
    badge.innerHTML = emoji;
    badge.setAttribute('contenteditable', 'false');
    
    const left = parseFloat(this.activeImg.style.left || '0') + parseFloat(this.activeImg.style.width || '0') - 20;
    const top = parseFloat(this.activeImg.style.top || '0') + parseFloat(this.activeImg.style.height || '0') - 10;
    
    badge.setAttribute('style', `position: absolute; left: ${left}px; top: ${top}px; background: white; border: 1px solid #dadce0; border-radius: 12px; padding: 2px 6px; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); z-index: 10;`);
    
    this.slideBodyRef?.nativeElement.appendChild(badge);
    if(this.activePage) this.activePage.body = this.slideBodyRef?.nativeElement.innerHTML;
    this.onChanged();
    
    this.showSlideMediaReactions = false;
  }

  openSlideEmojiPicker(event: Event) {
    event.stopPropagation();
    this.showSlideEmojiPickerModal = true;
    this.showSlideMediaReactions = false;
  }

  onSlideEmojiSelect(emoji: string) {
    this.addSlideMediaReaction(emoji);
    if (!this.slideReactionEmojis.includes(emoji)) {
        this.slideReactionEmojis.pop();
        this.slideReactionEmojis.unshift(emoji);
    }
    this.showSlideEmojiPickerModal = false;
  }

"""
if 'triggerVideoInsert' not in content:
    idx = content.rfind('}')
    content = content[:idx] + vid_methods_new + content[idx:]

# 4. Modify mousedown to select video
mousedown_old = """if (target.tagName === 'IMG' || target.classList.contains('canvas-shape') || target.classList.contains('canvas-textbox')) {"""
mousedown_new = """if (target.tagName === 'IMG' || target.tagName === 'VIDEO' || target.classList.contains('canvas-shape') || target.classList.contains('canvas-textbox')) {"""
content = content.replace(mousedown_old, mousedown_new)

# 5. Add overlay buttons for Slide editor
overlay_old = """      <!-- Selection Box -->
      <div class="selection-box" *ngIf="activeImg"
           [style.left.px]="activeImgRect.left" [style.top.px]="activeImgRect.top"
           [style.width.px]="activeImgRect.width" [style.height.px]="activeImgRect.height">
        <div class="resize-handle tl" (mousedown)="startResize($event, 'tl')"></div>
        <div class="resize-handle tr" (mousedown)="startResize($event, 'tr')"></div>
        <div class="resize-handle bl" (mousedown)="startResize($event, 'bl')"></div>
        <div class="resize-handle br" (mousedown)="startResize($event, 'br')"></div>
      </div>"""
overlay_new = """      <!-- Selection Box -->
      <div class="selection-box" *ngIf="activeImg"
           [style.left.px]="activeImgRect.left" [style.top.px]="activeImgRect.top"
           [style.width.px]="activeImgRect.width" [style.height.px]="activeImgRect.height"
           style="position: relative;">
        <div class="resize-handle tl" (mousedown)="startResize($event, 'tl')"></div>
        <div class="resize-handle tr" (mousedown)="startResize($event, 'tr')"></div>
        <div class="resize-handle bl" (mousedown)="startResize($event, 'bl')"></div>
        <div class="resize-handle br" (mousedown)="startResize($event, 'br')"></div>
        
        <div class="slide-media-actions" *ngIf="activeImg.tagName === 'IMG' || activeImg.tagName === 'VIDEO'" style="position: absolute; top: -36px; right: -2px; display: flex; gap: 4px; background: white; border-radius: 4px; padding: 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.2); pointer-events: auto; align-items: center; white-space: nowrap;">
           <button class="header-icon-btn" (click)="downloadSelectedSlideMedia()" title="Download" style="background:none;border:none;cursor:pointer;"><span class="material-symbols-outlined" style="font-size: 18px;">download</span></button>
           <div style="width: 1px; background: #dadce0; margin: 2px 4px;"></div>
           <button class="header-icon-btn" (click)="toggleSlideMediaReactions($event)" title="Add Reaction" style="position: relative; overflow: visible; background:none;border:none;cursor:pointer;">
               <span class="material-symbols-outlined" style="font-size: 18px;">add_reaction</span>
               <div *ngIf="showSlideMediaReactions" class="doc-media-reactions-popover" style="position: absolute; top: -45px; right: 0; background: white; border: 1px solid #dadce0; border-radius: 20px; padding: 4px 8px; display: flex; gap: 6px; z-index: 200; box-shadow: 0 4px 12px rgba(0,0,0,0.15); align-items: center;">
                   <span *ngFor="let emoji of slideReactionEmojis" (click)="addSlideMediaReaction(emoji); $event.stopPropagation()" style="cursor: pointer; font-size: 16px;">{{ emoji }}</span>
                   <span class="material-symbols-outlined" style="font-size:16px; cursor:pointer; color:#5f6368;" title="More Emojis" (click)="openSlideEmojiPicker($event)">add_reaction</span>
                   <span class="material-symbols-outlined" style="font-size:16px; cursor:pointer; color:#5f6368;" title="Close" (click)="showSlideMediaReactions = false; $event.stopPropagation()">close</span>
               </div>
           </button>
           <div *ngIf="showSlideEmojiPickerModal" class="reaction-emoji-picker-popup" style="position: absolute; top: -250px; right: 0; z-index: 300; width: 260px; height: 220px; background: white; border: 1px solid #dadce0; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.25); overflow: hidden; display: flex; flex-direction: column;" (click)="$event.stopPropagation()">
               <div style="display:flex; justify-content:space-between; align-items:center; padding: 4px 8px; background: #f8f9fa; border-bottom: 1px solid #dadce0;">
                   <span style="font-size: 11px; font-weight: 600; color: #5f6368;">Select Emoji</span>
                   <span class="material-symbols-outlined" style="font-size: 16px; cursor: pointer; color: #5f6368;" title="Close" (click)="showSlideEmojiPickerModal = false">close</span>
               </div>
               <app-media-picker [onlyEmojis]="true" [pickerHeight]="'190px'" [darkMode]="false" (emojiSelect)="onSlideEmojiSelect($event)"></app-media-picker>
           </div>
        </div>
      </div>"""
content = content.replace(overlay_old, overlay_new)

with open("frontend/src/app/pages/slide-editor/slide-editor.component.ts", "w", encoding="utf-8") as f:
    f.write(content)
