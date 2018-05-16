;; these are custom VOCO Emacs functions, you should copy them from here to your Emacs init file




(defun voco-copy-line (arg)
  "Copy lines (as many as prefix argument) in the kill ring"
  ;; (interactive "p")
  (kill-ring-save (line-beginning-position)
                  (line-beginning-position (+ 1 arg))))

  ;; (message "%d line%s copied" arg (if (= 1 arg) "" "s")))
(defun copy-file-name-to-clipboard ()
  "Copy the current buffer file name to the clipboard."
  (interactive)
  (let ((filename (if (equal major-mode 'dired-mode)
                      default-directory
                    (buffer-file-name))))
    (when filename
      (kill-new filename)
      (message "Copied buffer file name '%s' to the clipboard." filename))))
