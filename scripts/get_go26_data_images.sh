# run sudo sshfs naoth@gruenau4.informatik.hu-berlin.de:/vol/repl261-vol4/naoth/logs/ /mnt/repl -o allow_other,ro,uid=33,gid=33,ServerAliveInterval=15,ServerAliveCountMax=3,reconnect -o IdentityFile=~/.ssh/id_ed25519

# Set up trap to exit script on Ctrl-C
trap "echo 'Script interrupted by user'; exit 1" SIGINT

file="combined.log" # **.mp4 combined.log game.log config.zip nao.info sensor.log
log_root="/mnt/logs2"

echo "2026-03-10-GO26/2026-03-11_11-50-00_Bit-Bots_vs_Berlin United"
rsync -av --size-only --include='extracted/***' --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2026-03-10-GO26/2026-03-11_11-50-00_Bit-Bots_vs_Berlin United_half1/' ${log_root}'/2026-03-10-GO26/2026-03-11_11-50-00_Bit-Bots_vs_Berlin United_half1/'
rsync -av --size-only --include='extracted/***' --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2026-03-10-GO26/2026-03-11_11-50-00_Bit-Bots_vs_Berlin United_half2/' ${log_root}'/2026-03-10-GO26/2026-03-11_11-50-00_Bit-Bots_vs_Berlin United_half2/'

echo "2026-03-10-GO26/2026-03-11_15-30-00_Berlin United_vs_Ruhrbot Devils"
rsync -av --size-only --include='extracted/***' --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2026-03-10-GO26/2026-03-11_15-30-00_Berlin United_vs_Ruhrbot Devils_half1/' ${log_root}'/2026-03-10-GO26/2026-03-11_15-30-00_Berlin United_vs_Ruhrbot Devils_half1/'
rsync -av --size-only ---include='extracted/***' --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2026-03-10-GO26/2026-03-11_15-30-00_Berlin United_vs_Ruhrbot Devils_half2/' ${log_root}'/2026-03-10-GO26/2026-03-11_15-30-00_Berlin United_vs_Ruhrbot Devils_half2/'

echo "2026-03-10-GO26/2026-03-12_13-00-00_R-ZWEI KICKERS_vs_Berlin United"
rsync -av --size-only --include='extracted/***' --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2026-03-10-GO26/2026-03-12_13-00-00_R-ZWEI KICKERS_vs_Berlin United_half1/' ${log_root}'/2026-03-10-GO26/2026-03-12_13-00-00_R-ZWEI KICKERS_vs_Berlin United_half1/'
rsync -av --size-only --include='extracted/***' --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2026-03-10-GO26/2026-03-12_13-00-00_R-ZWEI KICKERS_vs_Berlin United_half2/' ${log_root}'/2026-03-10-GO26/2026-03-12_13-00-00_R-ZWEI KICKERS_vs_Berlin United_half2/'

echo "2026-03-10-GO26/2026-03-12_16-20-00_Berlin United_vs_WF Wolves"
rsync -av --size-only --include='extracted/***' --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2026-03-10-GO26/2026-03-12_16-20-00_Berlin United_vs_WF Wolves_half1/' ${log_root}'/2026-03-10-GO26/2026-03-12_16-20-00_Berlin United_vs_WF Wolves_half1/'
rsync -av --size-only --include='extracted/***' --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2026-03-10-GO26/2026-03-12_16-20-00_Berlin United_vs_WF Wolves_half2/' ${log_root}'/2026-03-10-GO26/2026-03-12_16-20-00_Berlin United_vs_WF Wolves_half2/'

echo "2026-03-10-GO26/2026-03-13_11-50-00_Berlin United_vs_ZJU Dancer"
rsync -av --size-only --include='extracted/***' --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2026-03-10-GO26/2026-03-13_11-50-00_Berlin United_vs_ZJU Dancer_half1/' ${log_root}'/2026-03-10-GO26/2026-03-13_11-50-00_Berlin United_vs_ZJU Dancer_half1/'
rsync -av --size-only --include='extracted/***' --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2026-03-10-GO26/2026-03-13_11-50-00_Berlin United_vs_ZJU Dancer_half2/' ${log_root}'/2026-03-10-GO26/2026-03-13_11-50-00_Berlin United_vs_ZJU Dancer_half2/'

echo "2026-03-10-GO26/2026-03-13_16-40-00_Berlin United_vs_WF Wolves"
rsync -av --size-only --include='extracted/***' --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2026-03-10-GO26/2026-03-13_16-40-00_Berlin United_vs_WF Wolves_half1/' ${log_root}'/2026-03-10-GO26/2026-03-13_16-40-00_Berlin United_vs_WF Wolves_half1/'
rsync -av --size-only --include='extracted/***' --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2026-03-10-GO26/2026-03-13_16-40-00_Berlin United_vs_WF Wolves_half2/' ${log_root}'/2026-03-10-GO26/2026-03-13_16-40-00_Berlin United_vs_WF Wolves_half2/'

echo "2026-03-10-GO26/2026-03-14_09-10-00_ZJU Dancer_vs_Berlin United"
rsync -av --size-only --include='extracted/***' --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2026-03-10-GO26/2026-03-14_09-10-00_ZJU Dancer_vs_Berlin United_half1/' ${log_root}'/2026-03-10-GO26/2026-03-14_09-10-00_ZJU Dancer_vs_Berlin United_half1/'
rsync -av --size-only --include='extracted/***' --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2026-03-10-GO26/2026-03-14_09-10-00_ZJU Dancer_vs_Berlin United_half2/' ${log_root}'/2026-03-10-GO26/2026-03-14_09-10-00_ZJU Dancer_vs_Berlin United_half2/'

echo "2026-03-10-GO26/2026-03-14_13-10-00_Berlin United_vs_R-ZWEI KICKERS"
rsync -av --size-only --include='extracted/***' --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2026-03-10-GO26/2026-03-14_13-10-00_Berlin United_vs_R-ZWEI KICKERS_half1/' ${log_root}'/2026-03-10-GO26/2026-03-14_13-10-00_Berlin United_vs_R-ZWEI KICKERS_half1/'
rsync -av --size-only --include='extracted/***' --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2026-03-10-GO26/2026-03-14_13-10-00_Berlin United_vs_R-ZWEI KICKERS_half2/' ${log_root}'/2026-03-10-GO26/2026-03-14_13-10-00_Berlin United_vs_R-ZWEI KICKERS_half2/'
