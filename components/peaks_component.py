from services.peaks_service import PeaksService

def reset_paeks(app):
    print(">> START:: reset_paeks")
    PeaksService().peaks_check_directory_existence()
    print(">> END:: reset_paeks")
