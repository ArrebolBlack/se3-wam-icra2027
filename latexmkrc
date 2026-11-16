# Build the companion document's labels when xr-hyper needs its .aux file.
# Based on Overleaf's xr recipe:
# https://www.overleaf.com/learn/how-to/Cross_referencing_with_the_xr_package_in_Overleaf
add_cus_dep('tex', 'aux', 0, 'build_external_labels');

sub build_external_labels {
    my ($source) = @_;
    return 0 if $source eq $root_filename;
    my ($name, $path) = fileparse($source);
    my $external_dir = 'build/external-labels';
    pushd($path);
    # The main paper and supplement reference each other. Do not load this
    # custom rule in the child, which would recursively rebuild the parent.
    my $status = system('latexmk', '-norc', '-pdf',
                        '-interaction=nonstopmode', '-halt-on-error',
                        "-outdir=$external_dir", "$name.tex");
    if ($status == 0) {
        copy("$external_dir/$name.aux", "$name.aux")
            or die "Cannot copy external labels for $name: $!";
        rdb_add_generated("$external_dir/$name.aux");
    }
    popd();
    return $status;
}
