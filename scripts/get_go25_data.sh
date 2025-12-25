# run sudo sshfs naoth@gruenau4.informatik.hu-berlin.de:/vol/repl261-vol4/naoth/logs/ /mnt/repl -o allow_other,ro,uid=33,gid=33,ServerAliveInterval=15,ServerAliveCountMax=3,reconnect -o IdentityFile=~/.ssh/id_ed25519

# Set up trap to exit script on Ctrl-C
trap "echo 'Script interrupted by user'; exit 1" SIGINT

file="combined.log" # **.mp4 combined.log game.log config.zip nao.info sensor.log
log_root="/mnt/e/logs"

echo "/mnt/repl/2025-03-12-GO25/2025-03-12_21-30-00_Berlin United_vs_Invisibles_half1-test"
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2025-03-12-GO25/2025-03-12_21-30-00_Berlin United_vs_Invisibles_half1-test/' ${log_root}'/2025-03-12-GO25/2025-03-12_21-30-00_Berlin United_vs_Invisibles_half1-test/'

echo "2025-03-12-GO25/2025-03-13_10-10-00_Berlin United_vs_Bembelbots"
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2025-03-12-GO25/2025-03-13_10-10-00_Berlin United_vs_Bembelbots_half1/' ${log_root}'/2025-03-12-GO25/2025-03-13_10-10-00_Berlin United_vs_Bembelbots_half1/'
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2025-03-12-GO25/2025-03-13_10-10-00_Berlin United_vs_Bembelbots_half2/' ${log_root}'/2025-03-12-GO25/2025-03-13_10-10-00_Berlin United_vs_Bembelbots_half2/'

echo "2025-03-12-GO25/2025-03-13_17-30-00_Berlin United_vs_HTWK Robots"
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2025-03-12-GO25/2025-03-13_17-30-00_Berlin United_vs_HTWK Robots_half1/' ${log_root}'/2025-03-12-GO25/2025-03-13_17-30-00_Berlin United_vs_HTWK Robots_half1/'
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2025-03-12-GO25/2025-03-13_17-30-00_Berlin United_vs_HTWK Robots_half2/' ${log_root}'/2025-03-12-GO25/2025-03-13_17-30-00_Berlin United_vs_HTWK Robots_half2/'

echo "2025-03-12-GO25/2025-03-14_10-10-00_Berlin United_vs_Nao Devils"
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2025-03-12-GO25/2025-03-14_10-10-00_Berlin United_vs_Nao Devils_half1/' ${log_root}'/2025-03-12-GO25/2025-03-14_10-10-00_Berlin United_vs_Nao Devils_half1/'
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2025-03-12-GO25/2025-03-14_10-10-00_Berlin United_vs_Nao Devils_half2/' ${log_root}'/2025-03-12-GO25/2025-03-14_10-10-00_Berlin United_vs_Nao Devils_half2/'

echo "2025-03-12-GO25/2025-03-14_15-10-00_Berlin United_vs_Dutch Nao Team"
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2025-03-12-GO25/2025-03-14_15-10-00_Berlin United_vs_Dutch Nao Team_half1/' ${log_root}'/2025-03-12-GO25/2025-03-14_15-10-00_Berlin United_vs_Dutch Nao Team_half1/'
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2025-03-12-GO25/2025-03-14_15-10-00_Berlin United_vs_Dutch Nao Team_half2/' ${log_root}'/2025-03-12-GO25/2025-03-14_15-10-00_Berlin United_vs_Dutch Nao Team_half2/'

echo "2025-03-12-GO25/2025-03-15_11-40-00_Berlin United_vs_B-Human"
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2025-03-12-GO25/2025-03-15_11-40-00_Berlin United_vs_B-Human_half1/' ${log_root}'/2025-03-12-GO25/2025-03-15_11-40-00_Berlin United_vs_B-Human_half1/'
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2025-03-12-GO25/2025-03-15_11-40-00_Berlin United_vs_B-Human_half2/' ${log_root}'/2025-03-12-GO25/2025-03-15_11-40-00_Berlin United_vs_B-Human_half2/'

echo "2025-03-12-GO25/2025-03-15_15-00-00_Berlin United_vs_Dutch Nao Team"
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2025-03-12-GO25/2025-03-15_15-00-00_Berlin United_vs_Dutch Nao Team_half1/' ${log_root}'/2025-03-12-GO25/2025-03-15_15-00-00_Berlin United_vs_Dutch Nao Team_half1/'
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2025-03-12-GO25/2025-03-15_15-00-00_Berlin United_vs_Dutch Nao Team_half2/' ${log_root}'/2025-03-12-GO25/2025-03-15_15-00-00_Berlin United_vs_Dutch Nao Team_half2/'

echo "2025-03-12-GO25/2025-03-15_17-15-00_Berlin United_vs_HULKs"
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2025-03-12-GO25/2025-03-15_17-15-00_Berlin United_vs_HULKs_half1/' ${log_root}'/2025-03-12-GO25/2025-03-15_17-15-00_Berlin United_vs_HULKs_half1/'
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' '/mnt/repl/2025-03-12-GO25/2025-03-15_17-15-00_Berlin United_vs_HULKs_half2/' ${log_root}'/2025-03-12-GO25/2025-03-15_17-15-00_Berlin United_vs_HULKs_half2/'
