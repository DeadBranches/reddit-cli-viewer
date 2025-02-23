use std log

def reddit [url: string] {
    let output_directorypath = 'post-archive' | path expand
    let python_file: path = 'main.py' | path expand
    
    if (($output_directorypath | path exists) == false) {
        log info "Output directory doesn't exist. Making directory"
        mkdir $output_directorypath
    }
    
    with-env { PYTHON_UTF8:1 } {
        python $python_file $url
    }
}
