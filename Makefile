test:
	python setup.py test

clean:
	$(RM) -r build dist src/cchardet/*.cpp src/cchardet.egg-info
