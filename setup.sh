install() {
	DEST=~/.local/share/rhythmbpx/plugins/pandora/
	SOURCE=$(dirname $0)

	# remove current version of plugin
	rm -rf ${DEST}

	# create it
	mkdir -p ${DEST}

	# install currect verion of plugin
	cp -rv ${SOURCE}/plugin/* ${DEST}

}

case "$1" in
	install)
		install
		;;
	*)
		install
		;;
esac

exit 0
