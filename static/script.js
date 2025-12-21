const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const processingArea = document.getElementById('processing-area');

document.addEventListener('DOMContentLoaded', async () => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(savedTheme);

    try {
        const res = await fetch('/api/check-ffmpeg');
        const data = await res.json();
        if (!data.installed) {
            showToast('⚠️ FFmpeg not found! Video conversion will not work.');
        }
    } catch (e) {
        console.log('FFmpeg check failed');
    }
});

function toggleTheme() {
    const html = document.documentElement;
    const isCurrentlyDark = html.classList.contains('dark');
    const newTheme = isCurrentlyDark ? 'light' : 'dark';
    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
}

function applyTheme(theme) {
    const html = document.documentElement;
    const body = document.body;
    const header = document.querySelector('header');
    const toggle = document.getElementById('theme-toggle');
    const knob = document.getElementById('toggle-knob');
    const main = document.querySelector('main');

    if (theme === 'light') {
        html.classList.remove('dark');
        html.classList.add('light');

        body.classList.remove('bg-black', 'text-gray-200');
        body.classList.add('bg-gradient-to-br', 'from-gray-50', 'via-white', 'to-gray-100', 'text-gray-900');

        if (header) {
            header.classList.remove('bg-black/80', 'border-white/10');
            header.classList.add('bg-white/90', 'border-gray-200', 'shadow-lg');
        }

        if (toggle) toggle.classList.replace('bg-gray-600', 'bg-blue-500');
        if (knob) knob.style.transform = 'translateX(24px)';

        document.querySelectorAll('.glass').forEach(el => {
            el.classList.remove('bg-white/5', 'border-white/10');
            el.classList.add('bg-white/80', 'border-gray-200', 'shadow-md');
        });

        document.querySelectorAll('.bg-white\\/10').forEach(el => {
            el.classList.remove('bg-white/10', 'hover:bg-white/20', 'border-white/10');
            el.classList.add('bg-gray-100', 'hover:bg-gray-200', 'border-gray-300', 'text-gray-800');
        });

        document.querySelectorAll('.bg-white\\/5').forEach(el => {
            el.classList.remove('bg-white/5', 'border-white/5');
            el.classList.add('bg-white', 'border-gray-200', 'shadow-sm');
        });

        document.querySelectorAll('.text-white').forEach(el => {
            if (!el.closest('button') && !el.closest('a')) {
                el.classList.remove('text-white');
                el.classList.add('text-gray-900');
            }
        });

    } else {
        html.classList.add('dark');
        html.classList.remove('light');

        body.classList.remove('bg-gradient-to-br', 'from-gray-50', 'via-white', 'to-gray-100', 'text-gray-900');
        body.classList.add('bg-black', 'text-gray-200');

        if (header) {
            header.classList.remove('bg-white/90', 'border-gray-200', 'shadow-lg');
            header.classList.add('bg-black/80', 'border-white/10');
        }

        if (toggle) toggle.classList.replace('bg-blue-500', 'bg-gray-600');
        if (knob) knob.style.transform = 'translateX(0)';

        document.querySelectorAll('.bg-white\\/80').forEach(el => {
            el.classList.remove('bg-white/80', 'border-gray-200', 'shadow-md');
            el.classList.add('bg-white/5', 'border-white/10');
        });

        document.querySelectorAll('.bg-gray-100').forEach(el => {
            el.classList.remove('bg-gray-100', 'hover:bg-gray-200', 'border-gray-300', 'text-gray-800');
            el.classList.add('bg-white/10', 'hover:bg-white/20', 'border-white/10');
        });

        document.querySelectorAll('.bg-white').forEach(el => {
            if (el.classList.contains('border-gray-200')) {
                el.classList.remove('bg-white', 'border-gray-200', 'shadow-sm');
                el.classList.add('bg-white/5', 'border-white/5');
            }
        });

        document.querySelectorAll('.text-gray-900').forEach(el => {
            if (!el.closest('button') && !el.closest('a')) {
                el.classList.remove('text-gray-900');
                el.classList.add('text-white');
            }
        });
    }
}

let conversionStats = { total: 0, success: 0, failed: 0 };

async function convertAll() {
    const buttons = document.querySelectorAll('[id^="actions-"] button');
    let count = 0;

    conversionStats = { total: 0, success: 0, failed: 0 };

    for (const btn of buttons) {
        if (btn.innerText.includes('Convert') || btn.innerText.includes('Dönüştür')) {
            count++;
        }
    }

    conversionStats.total = count;
    updateConversionCounter();

    for (const btn of buttons) {
        if (btn.innerText.includes('Convert') || btn.innerText.includes('Dönüştür')) {
            btn.click();
            await new Promise(r => setTimeout(r, 500));
        }
    }

    if (count > 0) {
        showToast(`${count} files converting...`);
    } else {
        showToast('No files to convert');
    }
}

function applyBatchFormat(format) {
    if (!format) return;

    const selects = document.querySelectorAll('[id^="format-"]');
    let applied = 0;

    selects.forEach(select => {
        const option = select.querySelector(`option[value="${format}"]`);
        if (option) {
            select.value = format;
            applied++;
        }
    });

    if (applied > 0) {
        showToast(`✓ ${format.toUpperCase()} applied to ${applied} files`);
    } else {
        showToast(`⚠️ ${format.toUpperCase()} cannot be applied to these file types`);
    }

    document.getElementById('batch-format').value = '';
}

function updateConversionCounter() {
    const counter = document.getElementById('conversion-counter');
    if (conversionStats.total > 0) {
        counter.textContent = `${conversionStats.success}/${conversionStats.total}`;
        counter.classList.remove('hidden');
    } else {
        counter.classList.add('hidden');
    }
}

function incrementSuccessCount() {
    conversionStats.success++;
    updateConversionCounter();

    if (conversionStats.success === conversionStats.total) {
        showToast(`✅ Complete! ${conversionStats.success}/${conversionStats.total} successful`);
    }
}

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('scale-[0.98]', 'ring-2', 'ring-blue-500', 'bg-blue-500/10');
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropZone.classList.remove('scale-[0.98]', 'ring-2', 'ring-blue-500', 'bg-blue-500/10');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('scale-[0.98]', 'ring-2', 'ring-blue-500', 'bg-blue-500/10');
    handleFiles(e.dataTransfer.files);
});

let dragCounter = 0;

document.addEventListener('dragenter', (e) => {
    e.preventDefault();
    dragCounter++;
    document.body.classList.add('ring-4', 'ring-inset', 'ring-blue-500/50');
});

document.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dragCounter--;
    if (dragCounter === 0) {
        document.body.classList.remove('ring-4', 'ring-inset', 'ring-blue-500/50');
    }
});

document.addEventListener('dragover', (e) => {
    e.preventDefault();
});

document.addEventListener('drop', (e) => {
    e.preventDefault();
    dragCounter = 0;
    document.body.classList.remove('ring-4', 'ring-inset', 'ring-blue-500/50');

    if (e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
    }
});

document.addEventListener('paste', (e) => {
    const files = e.clipboardData?.files;
    if (files && files.length > 0) {
        e.preventDefault();
        showToast(`📋 Pasting ${files.length} files...`);
        handleFiles(files);
    }
});

const MAX_FILE_SIZE = 100 * 1024 * 1024;

function checkFileSize(file) {
    if (file.size > MAX_FILE_SIZE) {
        showToast(`⚠️ "${file.name}" cok buyuk (${(file.size / 1024 / 1024).toFixed(0)}MB)`);
        return false;
    }
    return true;
}

const translations = {
    tr: {
        title: "Evrensel Dönüştürücü",
        heroTitle: "Her Şeyi Dönüştür ⚡",
        heroSubtitle: "Güvenli, Hızlı ve Modern. Dosyalarınız cihazınızdan asla çıkmaz.",
        dropText: "Dosyaları buraya bırakın",
        browseText: "veya seçmek için tıklayın",
        convertAll: "Tümünü Dönüştür",
        downloadAll: "Toplu İndir (ZIP)",
        applyAll: "Tümüne Uygula",
        features: {
            image: "Resim",
            video: "Video",
            audio: "Ses",
            document: "Döküman",
            archive: "Arşiv",
            data: "Veri"
        },
        status: {
            waiting: "Bekliyor...",
            converting: "Dönüştürülüyor...",
            success: "Başarılı",
            error: "Hata"
        },
        buttons: {
            convert: "Dönüştür",
            retry: "Tekrar Dene",
            remove: "Kaldır",
            download: "İndir",
            convertAgain: "Başka Formata Dönüştür",
            back: "← Geri",
            addFile: "+ Dosya Ekle",
            applyToAll: "Tümüne Uygula"
        },
        featuresUI: {
            titles: ["65+ Format", "Işık Hızında", "Gizlilik Odaklı", "Premium Kalite"],
            descs: ["Resim, Video, Ses, Belge ve Arşiv.", "GPU destekli hızlı dönüştürme.", "%100 yerel, dosyalarınız sizde.", "Kaliteden ödün vermeden optimize."]
        },
        groups: {
            image: "📸 Resim",
            video: "🎬 Video",
            audio: "🎵 Ses",
            document: "📄 Döküman",
            archive: "📦 Arşiv",
            data: "📊 Veri"
        },
        toasts: {
            ffmpegMissing: "⚠️ FFmpeg bulunamadı! Video dönüştürme çalışmayacak.",
            downloadStarted: "Toplu indirme başladı!",
            zipError: "Hata: Zip oluşturulamadı",
            connError: "Bağlantı hatası",
            converting: "dosya dönüştürülüyor...",
            noFiles: "Dönüştürülecek dosya yok",
            batchSuccess: "dosyaya formatı uygulandı",
            batchError: "bu dosya türlerine uygulanamaz",
            completed: "Tamamlandı!",
            pasting: "dosya yapıştırılıyor...",
            tooLarge: "çok büyük",
            duplicate: "zaten yüklendi, atlanıyor...",
            fileRemoved: "kaldırıldı",
            error: "Hata"
        }
    },
    en: {
        title: "Universal Converter",
        heroTitle: "Convert Anything ⚡",
        heroSubtitle: "Secure, Fast and Modern. Your files never leave your device.",
        dropText: "Drop files here",
        browseText: "or click to browse",
        convertAll: "Convert All",
        downloadAll: "Download All (ZIP)",
        applyAll: "Apply All",
        features: {
            image: "Image",
            video: "Video",
            audio: "Audio",
            document: "Document",
            archive: "Archive",
            data: "Data"
        },
        status: {
            waiting: "Waiting...",
            converting: "Converting...",
            success: "Success",
            error: "Error"
        },
        buttons: {
            convert: "Convert",
            retry: "Retry",
            remove: "Remove",
            download: "Download",
            convertAgain: "Convert Another Format",
            back: "← Back",
            addFile: "+ Add File",

        },
        featuresUI: {
            titles: ["65+ Formats", "Lightning Fast", "Privacy First", "Premium Quality"],
            descs: ["Image, Video, Audio, Doc, Archive.", "GPU accelerated conversion.", "100% local, files stay with you.", "Optimized without quality loss."]
        },
        groups: {
            image: "📸 Image",
            video: "🎬 Video",
            audio: "🎵 Audio",
            document: "📄 Document",
            archive: "📦 Archive",
            data: "📊 Data"
        },
        toasts: {
            ffmpegMissing: "⚠️ FFmpeg not found! Video conversion disabled.",
            downloadStarted: "Batch download started!",
            zipError: "Error: Could not create Zip",
            connError: "Connection error",
            converting: "files converting...",
            noFiles: "No files to convert",
            batchSuccess: "format applied to files",
            batchError: "cannot be applied to these file types",
            completed: "Completed!",
            pasting: "files pasting...",
            tooLarge: "too large",
            duplicate: "already uploaded, skipping...",
            fileRemoved: "removed",
            error: "Error"
        }
    }
};

let currentLang = localStorage.getItem('lang') || 'en';
function updateFeatureTexts(t) {
    const features = document.querySelectorAll('#features-section > div');

    if (features.length >= 4 && t.featuresUI) {
        for (let i = 0; i < 4; i++) {
            features[i].querySelector('h3').textContent = t.featuresUI.titles[i];
            features[i].querySelector('p').textContent = t.featuresUI.descs[i];
        }
    }
}

const uploadedFileNames = new Set();
const fileRegistry = new Map();
const fileDataStore = new Map();

const typeToGroupLabel = {
    'image': '📸',
    'video': '🎬',
    'audio': '🎵',
    'pdf': '📄',
    'document': '📄',
    'data': '📊',
    'archive': '📦'
};

function updateBatchVisibility() {
    const batchSelect = document.getElementById('batch-format');
    const optgroups = batchSelect.querySelectorAll('optgroup');

    const activeTypes = new Set(fileRegistry.values());

    if (activeTypes.size === 0) {
        optgroups.forEach(g => g.style.display = '');
        return;
    }

    optgroups.forEach(group => {
        const label = group.label;
        let shouldShow = false;

        for (const type of activeTypes) {
            if (typeToGroupLabel[type] === label) {
                shouldShow = true;
                break;
            }
        }

        group.style.display = shouldShow ? '' : 'none';

        if (!shouldShow && batchSelect.value) {
            const selectedOption = group.querySelector(`option[value="${batchSelect.value}"]`);
            if (selectedOption && selectedOption.selected) {
                batchSelect.value = "";
            }
        }
    });
}

async function handleFiles(files) {
    if (files.length > 0) {
        dropZone.classList.add('hidden');
        document.getElementById('hero-section')?.classList.add('hidden');
        processingArea.classList.remove('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    for (const file of files) {
        if (uploadedFileNames.has(file.name)) {
            showToast(`⚠️ "${file.name}" already uploaded, skipping...`);
            continue;
        }

        if (file.size > MAX_FILE_SIZE) {
            showToast(`⚠️ "${file.name}" large file (${(file.size / 1024 / 1024).toFixed(0)}MB) - may take a while`);
        }

        uploadedFileNames.add(file.name);

        const fileId = Math.random().toString(36).substring(7);
        createFileCard(file, fileId);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                updateCardWithOptions(fileId, data);
            } else {
                updateCardError(fileId, "Upload failed");
                uploadedFileNames.delete(file.name);
            }
        } catch (error) {
            updateCardError(fileId, "Server error");
            uploadedFileNames.delete(file.name);
        }
    }
}

async function downloadAll() {
    const downloadLinks = document.querySelectorAll('#processing-area a[download]');
    const filenames = Array.from(downloadLinks).map(a => {
        return a.getAttribute('href').split('/').pop();
    });

    if (filenames.length === 0) {
        showToast('No converted files to download');
        return;
    }

    showToast(`${filenames.length} files zipping...`);

    try {
        const response = await fetch('/api/download-all', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filenames: filenames })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "converted_files.zip";
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            showToast('Download started!');
        } else {
            showToast('Error: Could not create ZIP');
        }
    } catch (e) {
        console.error(e);
        showToast('Connection error');
    }
}

function checkDownloadAllButton() {
    const downloadBtns = document.querySelectorAll('#processing-area a[download]');
    const batchDownloadBtn = document.getElementById('btn-download-all');

    if (downloadBtns.length > 0) {
        batchDownloadBtn.classList.remove('hidden');
    }
}

function createFileCard(file, id) {
    const card = document.createElement('div');
    card.id = `card-${id}`;
    card.className = "glass rounded-2xl p-4 flex items-center justify-between transition-all duration-300 animate-pulse-subtle";

    card.innerHTML = `
        <div class="flex items-center space-x-4">
            <div class="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center text-xl">
                ⏳
            </div>
            <div>
                <h3 class="text-white font-medium text-sm truncate max-w-xs">${file.name}</h3>
                <p class="text-gray-500 text-xs">Loading...</p>
            </div>
        </div>
    `;
    processingArea.appendChild(card);
}

function updateCardWithOptions(id, data) {
    const card = document.getElementById(`card-${id}`);
    card.classList.remove('animate-pulse-subtle');

    let icon = '📄';
    let formatOptions = '';
    const t = translations[currentLang];

    if (data.type === 'image') {
        icon = '🖼️';
        formatOptions = `
            <option value="webp">WEBP</option>
            <option value="png">PNG</option>
            <option value="jpg">JPG</option>
            <option value="jpeg">JPEG</option>
            <option value="gif">GIF</option>
            <option value="bmp">BMP</option>
            <option value="tiff">TIFF</option>
            <option value="ico">ICO</option>
            <option value="avif">AVIF</option>
            <option value="pdf">PDF</option>
        `;
    } else if (data.type === 'video') {
        icon = '🎬';
        formatOptions = `
            <option value="mp4">MP4</option>
            <option value="webm">WEBM</option>
            <option value="avi">AVI</option>
            <option value="mkv">MKV</option>
            <option value="mov">MOV</option>
            <option value="wmv">WMV</option>
            <option value="flv">FLV</option>
            <option value="m4v">M4V</option>
            <option value="3gp">3GP</option>
            <option value="mpeg">MPEG</option>
            <option value="mp3">MP3</option>
            <option value="wav">WAV</option>
            <option value="gif">GIF</option>
        `;
    } else if (data.type === 'audio') {
        icon = '🎵';
        formatOptions = `
            <option value="mp3">MP3</option>
            <option value="wav">WAV</option>
            <option value="aac">AAC</option>
            <option value="ogg">OGG</option>
            <option value="flac">FLAC</option>
            <option value="m4a">M4A</option>
            <option value="wma">WMA</option>
            <option value="aiff">AIFF</option>
            <option value="opus">OPUS</option>
            <option value="ac3">AC3</option>
            <option value="m4r">M4R</option>
        `;
    } else if (data.type === 'data') {
        icon = '📊';
        formatOptions = `
            <option value="csv">CSV</option>
            <option value="xlsx">XLSX</option>
            <option value="json">JSON</option>
            <option value="txt">TXT</option>
            <option value="xml">XML</option>
            <option value="html">HTML</option>
        `;
    } else if (data.type === 'pdf') {
        icon = '📕';
        formatOptions = `
            <option value="txt">TXT</option>
            <option value="docx">DOCX</option>
            <option value="doc">DOC</option>
            <option value="html">HTML</option>
            <option value="md">MD</option>
            <option value="rtf">RTF</option>
        `;
    } else if (data.type === 'archive') {
        icon = '📦';
        formatOptions = `
            <option value="zip">ZIP</option>
            <option value="7z">7Z</option>
            <option value="tar">TAR</option>
        `;
    } else {
        icon = '📁';
        formatOptions = `
            <option value="txt">TXT</option>
        `;
    }

    card.innerHTML = `
        <div class="flex items-center space-x-4 w-full">
            <div class="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center text-2xl shadow-inner">
                ${icon}
            </div>
            <div class="flex-1">
                <h3 class="text-white font-medium text-sm truncate max-w-xs">${data.original_name}</h3>
                <div class="flex items-center space-x-2 mt-1">
                    <span class="text-xs text-gray-500 bg-white/5 px-2 py-0.5 rounded text-[10px] tracking-wider uppercase">${data.extension}</span>
                    <span class="text-gray-600 text-[10px]">${(data.size / 1024 / 1024).toFixed(2)} MB</span>
                </div>
            </div>
            <div class="flex items-center space-x-2" id="actions-${id}">
                <select id="format-${id}" class="bg-white/5 border border-white/10 text-white text-xs rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-apple-accent">
                    ${formatOptions}
                </select>
                <button onclick="startConversion('${id}', '${data.filename}')" class="px-4 py-2 rounded-lg bg-apple-accent hover:bg-blue-600 text-white text-xs font-medium transition-colors">
                    ${translations[currentLang].buttons.convert}
                </button>
                <button onclick="removeFile('${id}', '${data.original_name}')" class="p-2 rounded-lg hover:bg-red-500/20 text-gray-400 hover:text-red-500 transition-all" title="${translations[currentLang].buttons.remove}">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                </button>
            </div>
        </div>
        
        <!-- Progress Bar -->
        <div id="progress-${id}" class="absolute bottom-0 left-0 h-1 bg-apple-accent transition-all duration-300 w-0 rounded-b-2xl"></div>
    `;

    fileRegistry.set(id, data.type);
    fileDataStore.set(id, data);
    updateBatchVisibility();
}

async function startConversion(id, filename) {
    const actionsDiv = document.getElementById(`actions-${id}`);
    const progressBar = document.getElementById(`progress-${id}`);
    const formatSelect = document.getElementById(`format-${id}`);
    const targetFormat = formatSelect.value;

    actionsDiv.innerHTML = `<span class="text-xs text-apple-accent animate-pulse">${translations[currentLang].status.converting}</span>`;

    try {
        const response = await fetch('/api/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                file_path: filename,
                target_format: targetFormat,
                quality: 'high'
            })
        });

        const result = await response.json();

        if (result.success) {
            progressBar.style.width = "100%";
            progressBar.classList.remove('bg-apple-accent');
            progressBar.classList.add('bg-apple-success');

            actionsDiv.innerHTML = `
                <div class="flex items-center space-x-2">
                     <button onclick="resetCard('${id}', '${filename}')" class="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition-colors group" title="${translations[currentLang].buttons.convertAgain}">
                        <svg class="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                    </button>
                    <a href="/api/download/${result.filename}" download class="px-3 py-2 rounded-lg bg-apple-success hover:bg-green-600 text-white text-xs font-medium transition-colors inline-flex items-center space-x-1">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                        <span>${translations[currentLang].buttons.download}</span>
                    </a>
                </div>
            `;

            incrementSuccessCount();
            checkDownloadAllButton();

        } else {
            actionsDiv.innerHTML = `
                <div class="flex flex-col items-end">
                    <span class="text-[10px] text-red-500 mb-1 font-medium error-shake">${result.error}</span>
                    <button onclick="resetCard('${id}', '${filename}')" class="px-3 py-1 bg-white/10 hover:bg-white/20 text-white text-[10px] rounded transition-colors border border-white/10">
                        Tekrar Dene
                    </button>
                </div>
            `;

            progressBar.classList.remove('bg-apple-accent');
            progressBar.classList.add('bg-red-500');
            progressBar.style.width = "100%";
        }

    } catch (error) {
        console.error(error);
        actionsDiv.innerHTML = `
             <div class="flex flex-col items-end">
                <span class="text-[10px] text-red-500 mb-1">Bağlantı Hatası</span>
                <button onclick="resetCard('${id}', '${filename}')" class="px-3 py-1 bg-white/10 hover:bg-white/20 text-white text-[10px] rounded transition-colors">
                    Tekrar Dene
                </button>
            </div>
        `;
    }
}

function resetCard(id, filename) {
    const fileData = fileDataStore.get(id);
    if (fileData) {
        const progressBar = document.getElementById(`progress-${id}`);
        if (progressBar) {
            progressBar.style.width = "0%";
            progressBar.classList.remove('bg-red-500', 'bg-green-500', 'bg-apple-success');
            progressBar.classList.add('bg-apple-accent');
        }
        updateCardWithOptions(id, fileData);
    }
}

function updateCardError(id, msg) {
    const card = document.getElementById(`card-${id}`);
    card.classList.remove('animate-pulse-subtle');
    card.classList.add('border', 'border-red-500', 'bg-red-500/5');

    card.innerHTML = `
        <div class="flex items-center space-x-4 w-full p-2">
            <div class="w-12 h-12 rounded-xl bg-red-500/10 flex items-center justify-center text-xl text-red-500">
                ⚠️
            </div>
            <div class="flex-1">
                <h3 class="text-white font-medium text-sm">${files.find(f => f.id === id)?.original_name || 'File'}</h3>
                <p class="text-red-400 text-xs mt-1">${msg}</p>
            </div>
            <button onclick="removeFile('${id}')" class="p-2 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
        </div>
    `;
}

function showToast(msg) {
    const toast = document.getElementById('toast');
    document.getElementById('toast-message').textContent = msg;
    toast.classList.remove('translate-y-24', 'opacity-0');
    setTimeout(() => {
        toast.classList.add('translate-y-24', 'opacity-0');
    }, 3000);
}

function goBack() {
    processingArea.classList.add('hidden');
    dropZone.classList.remove('hidden');
    document.getElementById('hero-section')?.classList.remove('hidden');
    uploadedFileNames.clear();
    const cards = processingArea.querySelectorAll('[id^="card-"]');
    cards.forEach(card => card.remove());
    document.getElementById('btn-download-all')?.classList.add('hidden');
}

function removeFile(id, filename) {
    const card = document.getElementById(`card-${id}`);
    if (card) {
        card.style.opacity = '0';
        card.style.transform = 'translateX(20px)';
        setTimeout(() => {
            card.remove();
            uploadedFileNames.delete(filename);
            fileRegistry.delete(id);
            fileDataStore.delete(id);
            updateBatchVisibility();
            showToast(`🗑️ "${filename}" removed`);
            const remainingCards = processingArea.querySelectorAll('[id^="card-"]');
            if (remainingCards.length === 0) {
                goBack();
            }
        }, 200);
    }
}

function setLanguage2(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);
    const t = translations[lang];

    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (t[key]) {
            el.textContent = t[key];
        } else if (t.buttons && t.buttons[key]) {
            el.textContent = t.buttons[key];
        }
    });

    const dropText = document.querySelector('[data-i18n="dropText"]');
    if (dropText) {
        dropText.innerHTML = `${t.dropText} <span class="text-apple-blue cursor-pointer hover:underline">${t.browseText}</span>`;
    }

    document.querySelectorAll('[id^="card-"]').forEach(card => {
        const btnConvert = card.querySelector('button[onclick^="startConversion"]');
        if (btnConvert) btnConvert.textContent = t.buttons.convert;

        const btnRemove = card.querySelector('button[onclick^="removeFile"]');
        if (btnRemove) btnRemove.title = t.buttons.remove;

        const linkDownload = card.querySelector('a[download] span');
        if (linkDownload) linkDownload.textContent = t.buttons.download;

        const btnResetTitle = card.querySelector('button[onclick^="resetCard"][title]');
        if (btnResetTitle && !btnResetTitle.textContent.trim()) btnResetTitle.title = t.buttons.convertAgain;

        const btnRetry = card.querySelector('button[onclick^="resetCard"]');
        if (btnRetry && btnRetry.textContent.trim()) btnRetry.textContent = t.buttons.retry;
    });

    document.querySelectorAll('.lang-btn').forEach(btn => {
        if (btn.dataset.lang === lang) {
            btn.classList.add('bg-white', 'text-black', 'shadow-sm');
            btn.classList.remove('text-gray-500', 'hover:text-white');
        } else {
            btn.classList.remove('bg-white', 'text-black', 'shadow-sm');
            btn.classList.add('text-gray-500', 'hover:text-white');
        }
    });

    document.title = t.title;
    updateFeatureTexts(t);
}

function applyBatchFormat(format) {
    if (!format) return;

    const selects = document.querySelectorAll('#processing-area select');
    let applied = 0;

    selects.forEach(select => {
        const option = select.querySelector(`option[value="${format}"]`);
        if (option) {
            select.value = format;
            applied++;
        }
    });

    document.getElementById('batch-format').value = '';

    if (applied > 0) {
        showToast(`✅ ${format.toUpperCase()} → ${applied} ${translations[currentLang].toasts.batchSuccess}`);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    setLanguage2(currentLang);
});
