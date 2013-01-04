install() {
	DEST=~/.local/share/rhythmbox/plugins/pandora/
	SOURCE=$(dirname $0)

	# remove current version of plugin
	rm -rf ${DEST}

	# create it
	mkdir -p ${DEST}
	mkdir -p ${DEST}/pandora/pithos/pandora/

	# install currect verion of plugin
	cp -rv ${SOURCE}/plugin/* ${DEST}
	cp -rv ${SOURCE}/pithos/pithos/pandora/* ${DEST}/pandora/pithos/pandora/
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
