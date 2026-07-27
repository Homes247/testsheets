import re

with open("frontend/src/app/pages/doc-editor/doc-editor.component.ts", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update image-actions HTML
html_old = """<div class="image-actions" *ngIf="selectedObject.tagName === 'IMG'" style="position: absolute; top: -36px; right: -2px; display: flex; gap: 4px; background: white; border-radius: 4px; padding: 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.2); pointer-events: auto;\">
           <button class="header-icon-btn" (click)="setWrapStyle('inline')" title="Inline"><span class="material-symbols-outlined" style="font-size: 18px;">format_align_justify</span></button>
           <button class="header-icon-btn" (click)="setWrapStyle('left')" title="Wrap Left"><span class="material-symbols-outlined" style="font-size: 18px;">format_align_left</span></button>
           <button class="header-icon-btn" (click)="setWrapStyle('right')" title="Wrap Right"><span class="material-symbols-outlined" style="font-size: 18px;">format_align_right</span></button>
           <button class="header-icon-btn" (click)="setWrapStyle('break')" title="Break Text"><span class="material-symbols-outlined" style="font-size: 18px;">wrap_text</span></button>
           <button class="header-icon-btn" (click)="setWrapStyle('absolute')" title="In Front of Text"><span class="material-symbols-outlined" style="font-size: 18px;">layers</span></button>
           <div style="width: 1px; background: #dadce0; margin: 2px 4px;"></div>
           <button class="header-icon-btn" (click)="openCropModal()" title="Crop Image"><span class="material-symbols-outlined" style="font-size: 18px;">crop</span></button>
         </div>"""

html_new = """<div class="image-actions" *ngIf="selectedObject.tagName === 'IMG' || selectedObject.tagName === 'VIDEO' || selectedObject.tagName === 'AUDIO'" style="position: absolute; top: -42px; right: -2px; display: flex; gap: 4px; background: white; border-radius: 4px; padding: 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.2); pointer-events: auto; align-items: center; white-space: nowrap;">
           <button class="header-icon-btn" (click)="setWrapStyle('inline')" title="Inline"><span class="material-symbols-outlined" style="font-size: 18px;">format_align_justify</span></button>
           <button class="header-icon-btn" (click)="setWrapStyle('left')" title="Wrap Left"><span class="material-symbols-outlined" style="font-size: 18px;">format_align_left</span></button>
           <button class="header-icon-btn" (click)="setWrapStyle('right')" title="Wrap Right"><span class="material-symbols-outlined" style="font-size: 18px;">format_align_right</span></button>
           <button class="header-icon-btn" (click)="setWrapStyle('break')" title="Break Text"><span class="material-symbols-outlined" style="font-size: 18px;">wrap_text</span></button>
           <button class="header-icon-btn" (click)="setWrapStyle('absolute')" title="In Front of Text"><span class="material-symbols-outlined" style="font-size: 18px;">layers</span></button>
           <div style="width: 1px; background: #dadce0; margin: 2px 4px;"></div>
           <button *ngIf="selectedObject.tagName === 'IMG'" class="header-icon-btn" (click)="openCropModal()" title="Crop Image"><span class="material-symbols-outlined" style="font-size: 18px;">crop</span></button>
           <button class="header-icon-btn" (click)="downloadSelectedMedia()" title="Download"><span class="material-symbols-outlined" style="font-size: 18px;">download</span></button>
           <div style="width: 1px; background: #dadce0; margin: 2px 4px;"></div>
           <button class="header-icon-btn" (click)="toggleDocMediaReactions($event)" title="Add Reaction" style="position: relative; overflow: visible;">
               <span class="material-symbols-outlined" style="font-size: 18px;">add_reaction</span>
               <div *ngIf="showDocMediaReactions" class="doc-media-reactions-popover" style="position: absolute; top: -45px; right: 0; background: white; border: 1px solid #dadce0; border-radius: 20px; padding: 4px 8px; display: flex; gap: 6px; z-index: 200; box-shadow: 0 4px 12px rgba(0,0,0,0.15); align-items: center;">
                   <span *ngFor="let emoji of docReactionEmojis" (click)="addDocMediaReaction(emoji); $event.stopPropagation()" style="cursor: pointer; font-size: 16px;">{{ emoji }}</span>
                   <span class="material-symbols-outlined" style="font-size:16px; cursor:pointer; color:#5f6368;" title="More Emojis" (click)="openDocEmojiPicker($event)">add_reaction</span>
                   <span class="material-symbols-outlined" style="font-size:16px; cursor:pointer; color:#5f6368;" title="Close" (click)="showDocMediaReactions = false; $event.stopPropagation()">close</span>
               </div>
           </button>
           <div *ngIf="showDocEmojiPickerModal" class="reaction-emoji-picker-popup" style="position: absolute; top: -250px; right: 0; z-index: 300; width: 260px; height: 220px; background: white; border: 1px solid #dadce0; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.25); overflow: hidden; display: flex; flex-direction: column;" (click)="$event.stopPropagation()">
               <div style="display:flex; justify-content:space-between; align-items:center; padding: 4px 8px; background: #f8f9fa; border-bottom: 1px solid #dadce0;">
                   <span style="font-size: 11px; font-weight: 600; color: #5f6368;">Select Emoji</span>
                   <span class="material-symbols-outlined" style="font-size: 16px; cursor: pointer; color: #5f6368;" title="Close" (click)="showDocEmojiPickerModal = false">close</span>
               </div>
               <app-media-picker [onlyEmojis]="true" [pickerHeight]="'190px'" [darkMode]="false" (emojiSelect)="onDocEmojiSelect($event)"></app-media-picker>
           </div>
         </div>"""
content = content.replace(html_old, html_new)

# 2. Update onVideoUpload
vid_old = """  onVideoUpload(event: Event) {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      const html = `<div contenteditable="false" style="display: inline-block; margin: 10px 0;"><video controls src="${url}" style="width: 100%; max-width: 500px;"></video></div><br>`;
      document.execCommand('insertHTML', false, html);
    }
    (event.target as HTMLInputElement).value = '';
  }"""
vid_new = """  onVideoUpload(event: Event) {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const dataUrl = e.target?.result as string;
        const html = `<div class="doc-media-wrapper" contenteditable="false" style="display: inline-block; margin: 10px 0; position: relative;"><video controls src="${dataUrl}" style="width: 100%; max-width: 500px; border-radius: 8px;"></video></div><br>`;
        document.execCommand('insertHTML', false, html);
      };
      reader.readAsDataURL(file);
    }
    (event.target as HTMLInputElement).value = '';
  }"""
content = content.replace(vid_old, vid_new)

# 3. Update onAudioUpload
aud_old = """  onAudioUpload(event: Event) {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      const html = `<div contenteditable="false" style="display: inline-block; margin: 10px 0;"><audio controls src="${url}" style="width: 100%; max-width: 300px;"></audio></div><br>`;
      document.execCommand('insertHTML', false, html);
    }
    (event.target as HTMLInputElement).value = '';
  }"""
aud_new = """  onAudioUpload(event: Event) {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const dataUrl = e.target?.result as string;
        const html = `<div class="doc-media-wrapper" contenteditable="false" style="display: inline-block; margin: 10px 0; position: relative;"><audio controls src="${dataUrl}" style="width: 100%; max-width: 300px; border-radius: 8px;"></audio></div><br>`;
        document.execCommand('insertHTML', false, html);
      };
      reader.readAsDataURL(file);
    }
    (event.target as HTMLInputElement).value = '';
  }"""
content = content.replace(aud_old, aud_new)

# 4. Update click handler to select VIDEO and AUDIO
click_old = """    if (target.tagName === 'IMG' || target.classList.contains('vmail-text-box') || target.closest('.vmail-text-box')) {"""
click_new = """    if (target.tagName === 'IMG' || target.tagName === 'VIDEO' || target.tagName === 'AUDIO' || target.classList.contains('vmail-text-box') || target.closest('.vmail-text-box')) {"""
content = content.replace(click_old, click_new)

click_sel_old = """      if (this.selectedObject.tagName !== 'IMG') {"""
click_sel_new = """      if (this.selectedObject.tagName !== 'IMG' && this.selectedObject.tagName !== 'VIDEO' && this.selectedObject.tagName !== 'AUDIO') {"""
content = content.replace(click_sel_old, click_sel_new)

# 5. Add new methods at the end of class
methods = """  // -- Media and Reaction methods --
  docReactionEmojis = ['👍', '❤️', '😂', '😲', '😢', '😡'];
  showDocMediaReactions = false;
  showDocEmojiPickerModal = false;

  downloadSelectedMedia() {
    if (!this.selectedObject) return;
    const src = this.selectedObject.getAttribute('src');
    if (!src) return;
    const a = document.createElement('a');
    a.href = src;
    a.download = 'media_file';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  toggleDocMediaReactions(event: Event) {
    event.stopPropagation();
    this.showDocMediaReactions = !this.showDocMediaReactions;
    this.showDocEmojiPickerModal = false;
  }

  addDocMediaReaction(emoji: string) {
    if (!this.selectedObject) return;
    const parent = this.selectedObject.parentElement;
    if (parent && parent.classList.contains('doc-media-wrapper')) {
       // Insert badge if missing, or update
       let badge = parent.querySelector('.media-reaction-badge');
       if (!badge) {
           badge = document.createElement('div');
           badge.className = 'media-reaction-badge';
           badge.setAttribute('contenteditable', 'false');
           badge.setAttribute('style', 'position: absolute; bottom: -12px; right: 8px; background: white; border: 1px solid #dadce0; border-radius: 12px; padding: 2px 6px; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); z-index: 10;');
           parent.appendChild(badge);
       }
       const currentHtml = badge.innerHTML;
       if (!currentHtml.includes(emoji)) {
           badge.innerHTML = currentHtml ? currentHtml + ' ' + emoji : emoji;
       }
       this.onChanged();
    } else {
       // Just in case parent doesn't have doc-media-wrapper, wrap it or append badge directly
       let badge = this.selectedObject.parentElement!.querySelector('.media-reaction-badge');
       if (!badge) {
           badge = document.createElement('div');
           badge.className = 'media-reaction-badge';
           badge.setAttribute('contenteditable', 'false');
           badge.setAttribute('style', 'position: absolute; bottom: -12px; right: 8px; background: white; border: 1px solid #dadce0; border-radius: 12px; padding: 2px 6px; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); z-index: 10;');
           this.selectedObject.parentElement!.style.position = 'relative';
           this.selectedObject.parentElement!.appendChild(badge);
       }
       const currentHtml = badge.innerHTML;
       if (!currentHtml.includes(emoji)) {
           badge.innerHTML = currentHtml ? currentHtml + ' ' + emoji : emoji;
       }
       this.onChanged();
    }
    this.showDocMediaReactions = false;
  }

  openDocEmojiPicker(event: Event) {
    event.stopPropagation();
    this.showDocEmojiPickerModal = true;
    this.showDocMediaReactions = false;
  }

  onDocEmojiSelect(emoji: string) {
    this.addDocMediaReaction(emoji);
    if (!this.docReactionEmojis.includes(emoji)) {
        this.docReactionEmojis.pop();
        this.docReactionEmojis.unshift(emoji);
    }
    this.showDocEmojiPickerModal = false;
  }

"""

if 'docReactionEmojis =' not in content:
    idx = content.rfind('}')
    content = content[:idx] + methods + content[idx:]

# 6. Make sure document click handler closes the popups
doc_click_old = """  private globalClickHandler = (e: MouseEvent) => {
    const target = e.target as HTMLElement;
    if (target && target.classList.contains('doc-comment-span')) {
      const comment = target.getAttribute('data-comment');
      if (comment) {
        this.showToast(`Comment: ${comment}`);
      }
    }
  };"""
doc_click_new = """  private globalClickHandler = (e: MouseEvent) => {
    const target = e.target as HTMLElement;
    if (target && target.classList.contains('doc-comment-span')) {
      const comment = target.getAttribute('data-comment');
      if (comment) {
        this.showToast(`Comment: ${comment}`);
      }
    }
    this.showDocMediaReactions = false;
    this.showDocEmojiPickerModal = false;
  };"""
content = content.replace(doc_click_old, doc_click_new)

# 7. When inserting image as block, make sure it has doc-media-wrapper
img_insert_old = """  insertImageAsBlock(url: string) {
    const html = `<div contenteditable="false" style="display: inline-block; margin: 10px 0;"><img src="${url}" style="width: 100%; max-width: 500px;" /></div><br>`;
    document.execCommand('insertHTML', false, html);
  }"""
img_insert_new = """  insertImageAsBlock(url: string) {
    const html = `<div class="doc-media-wrapper" contenteditable="false" style="display: inline-block; margin: 10px 0; position: relative;"><img src="${url}" style="width: 100%; max-width: 500px; border-radius: 8px;" /></div><br>`;
    document.execCommand('insertHTML', false, html);
  }"""
content = content.replace(img_insert_old, img_insert_new)


with open("frontend/src/app/pages/doc-editor/doc-editor.component.ts", "w", encoding="utf-8") as f:
    f.write(content)
