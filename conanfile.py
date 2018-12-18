from conans import ConanFile, CMake, tools, Meson
from conanos.build import config_scheme
import os

class GstpluginsgoodConan(ConanFile):
    name = "gst-plugins-good"
    version = "1.14.4"
    description = "'Good' GStreamer plugins and helper libraries"
    url = "https://github.com/conanos/gst-plugins-good"
    homepage = "https://github.com/GStreamer/gst-plugins-good"
    license = "LGPL-2.1"
    generators = "gcc","visual_studio"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        'fPIC': [True, False]
    }
    default_options = { 'shared': True, 'fPIC': True }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def requirements(self):
        self.requires.add("glib/2.58.1@conanos/stable")
        self.requires.add("gstreamer/1.14.4@conanos/stable")
        self.requires.add("gst-plugins-base/1.14.4@conanos/stable")
        self.requires.add("libpng/1.6.34@conanos/stable")
        self.requires.add("speex/1.2.0@conanos/stable")
        self.requires.add("libsoup/2.65.1@conanos/stable")
        self.requires.add("mpg123/1.25.10@conanos/stable")
        self.requires.add("lame/3.100@conanos/stable")
        self.requires.add("orc/0.4.28@conanos/stable")
        self.requires.add("wavpack/5.1.0@conanos/stable")
        self.requires.add("flac/1.3.2@conanos/stable")
        self.requires.add("taglib/1.11.1@conanos/stable")
        self.requires.add("bzip2/1.0.6@conanos/stable")
        self.requires.add("zlib/1.2.11@conanos/stable")
        self.requires.add("libvpx/1.7.0@conanos/stable")
        self.requires.add("cairo/1.15.12@conanos/stable")
        #libjpeg-turbo
        #gdk-pixbuf
        #libdv
    def build_requirements(self):
        self.build_requires("libffi/3.299999@conanos/stable")
        self.build_requires("freetype/2.9.1@conanos/stable")
        self.build_requires("fontconfig/2.13.0@conanos/stable")
        self.build_requires("pixman/0.34.0@conanos/stable")
        self.build_requires("expat/2.2.5@conanos/stable")
        self.build_requires("libxml2/2.9.8@conanos/stable")

    def source(self):
        remotes = {'origin': 'https://github.com/GStreamer/gst-plugins-good.git'}
        extracted_dir = self.name + "-" + self.version
        tools.mkdir(extracted_dir)
        with tools.chdir(extracted_dir):
            self.run('git init')
            for key, val in remotes.items():
                self.run("git remote add %s %s"%(key, val))
            self.run('git fetch --all')
            self.run('git reset --hard %s'%(self.version))
            self.run('git submodule update --init --recursive')
            #self.run('git am %s'%(os.path.join('..',self.patch)))
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        deps=["glib","gstreamer","gst-plugins-base","libpng","speex","libsoup","mpg123","lame","orc","wavpack","flac",
              "taglib","bzip2","zlib","libvpx","cairo","libffi","freetype","fontconfig","pixman","expat","libxml2"]
        pkg_config_paths=[ os.path.join(self.deps_cpp_info[i].rootpath, "lib", "pkgconfig") for i in deps ]
        libpath = [ os.path.join(self.deps_cpp_info[i].rootpath, "lib") for i in ["bzip2","lame"] ]
        binpath = [ os.path.join(self.deps_cpp_info[i].rootpath, "bin") for i in ["orc"] ]
        include = [ os.path.join(self.deps_cpp_info["cairo"].rootpath, "include","cairo"),
                    os.path.join(self.deps_cpp_info["libsoup"].rootpath, "include","libsoup-2.4"),
                    os.path.join(self.deps_cpp_info["bzip2"].rootpath, "include"), ]
        prefix = os.path.join(self.build_folder, self._build_subfolder, "install")
        defs = {'prefix' : prefix}
        if self.settings.os == "Linux":
            defs.update({'libdir':'lib'})
        meson = Meson(self)
        if self.settings.os == 'Windows':
            with tools.environment_append({
                'PATH' : os.pathsep.join(binpath + [os.getenv('PATH')]),
                'LIB' : os.pathsep.join(libpath + [os.getenv('LIB')]),
                'INCLUDE' : os.pathsep.join(include + [os.getenv('INCLUDE')]),
                }):
                meson.configure(defs=defs,source_dir=self._source_subfolder, build_dir=self._build_subfolder,
                                pkg_config_paths=pkg_config_paths)
                meson.build()
                self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        self.copy("*", dst=self.package_folder, src=os.path.join(self.build_folder,self._build_subfolder, "install"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

