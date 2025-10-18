default:
  just run

run:
  python3 main.py -f examples/scenario1.json

build:
  python -m nuitka --onefile --lto=yes --clang --python-flag=-O main.py

run-bin:
	@if [ -f ./main.bin ]; then \
		./main.bin -f examples/scenario1.json; \
	else \
		python3 -m nuitka --onefile --lto=yes --clang --python-flag=-O main.py; \
		./main.bin; \
	fi
