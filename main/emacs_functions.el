;; (defun voco-copy-line (&optional arg)
;;       "Copy the whole line that point is on and move to the beginning of the next line.
;;     Consecutive calls to this command append each line to the
;;     kill-ring."
;;       (interactive)
;;       (let ((beg (line-beginning-position 1))
;;             (end (line-beginning-position 2)))
;;         (if (eq last-command 'quick-copy-line)
;;             (kill-append (buffer-substring beg end) (< end beg))
;;           (kill-new (buffer-substring beg end))))
;;       (beginning-of-line 2))

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
