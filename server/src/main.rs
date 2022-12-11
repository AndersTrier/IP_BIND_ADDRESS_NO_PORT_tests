use async_std::net::{TcpListener, TcpStream};
use futures::stream::StreamExt;
use std::error;
use std::cmp::min;
use std::time::Duration;
use async_std::task;
use rlimit::*;

// Number of open file descriptors allowed
const RLIMIT_NOFILE: u64 = 200000;


async fn handle_client(mut _stream: TcpStream) -> Result<(), Box<dyn error::Error>>{
    task::sleep(Duration::from_secs( 60 * 5 )).await;
    Ok(())
}


fn raise_rlimit_nofile() -> std::io::Result<()> {
    // Allow this process to have many open connections (file descriptors)
    // Check GETRLIMIT(2) - RLIMIT_NOFILE for more info
    let (nofile_soft, nofile_hard) = getrlimit(Resource::NOFILE)?;
    if nofile_soft < RLIMIT_NOFILE {
        // GETRLIMIT(2):
        // The hard limit acts  as  a  ceiling  for  the  soft
        // limit:  an  unprivileged process may set only its soft limit to a value
        // in the range from 0 up to the hard limit
        let newlimit = min(RLIMIT_NOFILE, nofile_hard);
        match setrlimit(Resource::NOFILE, newlimit, nofile_hard) {
            Ok(()) => println!("Raised RLIMIT_NOFILE from {} to {}", nofile_soft, newlimit),
            Err(error) => return Err(error)
        }
    }
    Ok(())
}


#[async_std::main]
async fn main() {
    raise_rlimit_nofile().unwrap_or_else(|error| {
        println!("Falied to update RLIMIT_NOFILE: {:?}. Continuing.", error);
    });

    let listener = TcpListener::bind("0.0.0.0:1337").await.unwrap();

    listener.incoming().for_each_concurrent(
        /* limit */ None,
        | tcpstream | async move {
            match tcpstream {
                Ok(stream) => {
                    if let Err(e) = handle_client(stream).await {
                        eprintln!("{}", e);
                    }
                }
                Err(e) => {
                    eprintln!("listener.incoming() error: {}", e);
                }
            }
        }
    ).await
}
