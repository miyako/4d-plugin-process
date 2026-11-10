#import <Carbon/Carbon.h>
#import <Cocoa/Cocoa.h>

// Force-included before every actual source, including the complete SDK.
@interface OwnershipURL : NSObject
- (id)initWithString:(NSString *)value;
- (id)initFileURLWithPath:(NSString *)value;
- (NSString *)absoluteString;
@end
@interface OwnershipImage : NSObject
- (id)initWithCGImage:(CGImageRef)image size:(NSSize)size;
- (NSData *)TIFFRepresentation;
@end
@interface OwnershipProcessInfo : NSObject
+ (id)processInfo;
- (NSArray *)arguments;
@end
@interface OwnershipWorkspace : NSObject
+ (id)sharedWorkspace;
- (NSArray *)launchedApplications;
@end
CFURLRef OwnershipCreateURL(CFAllocatorRef, CFStringRef, CFURLPathStyle, Boolean);
CFStringRef OwnershipCopyPath(CFURLRef, CFURLPathStyle);
int OwnershipSetenv(const char *, const char *, int);
char *OwnershipGetenv(const char *);
OSStatus OwnershipCurrentProcess(ProcessSerialNumber *);
OSStatus OwnershipProcessPID(const ProcessSerialNumber *, pid_t *);

#define NSURL OwnershipURL
#define NSImage OwnershipImage
#define NSProcessInfo OwnershipProcessInfo
#define NSWorkspace OwnershipWorkspace
#define CFURLCreateWithFileSystemPath OwnershipCreateURL
#define CFURLCopyFileSystemPath OwnershipCopyPath
#define setenv OwnershipSetenv
#define getenv OwnershipGetenv
#define GetCurrentProcess OwnershipCurrentProcess
#define GetProcessPID OwnershipProcessPID
