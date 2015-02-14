# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def add_mission_statement_content(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    FlatPage = apps.get_model("flatpages", "FlatPage")
    mission_statement = FlatPage.objects.get(template_name='flatpages/mission-statement.html')
    mission_statement.content = """<p>The intention and purpose of this website is ultimately dedicated to the <strong>betterment of Mankind through the
      dissemination of this music</strong>. Our hope is that the music on this site is studied and enjoyed by people of
      open minds and clear thoughts. We ask that you research the artists and, if you enjoy their music, to
      support them by buying their cds or contacting them with positive feedback. We dedicate this site as a
      <strong>resource for musicians and fans</strong> to discover each others work and to share ideas. <strong>Through peaceful
      interchange we will be able to progress as Artists and as Human Beings.</strong></p>

    <p>Our intention is also to support Smalls Jazz Club and the Artists that perform there. By supporting this
      site, you are directly supporting the club and its Artists. We hope that if you are able to, that you come
      visit us in New York City and experience the club in person.</p>

    <p>We ask that you not steal from this site and that you treat the material here <strong>respectfully</strong>. Much of the
      content on this site is here by the <strong>goodwill of the Artists</strong> who have performed at the club.</p>"""

    mission_statement.save()


def add_about_us_content(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    FlatPage = apps.get_model("flatpages", "FlatPage")
    about_us = FlatPage.objects.get(template_name='flatpages/about-us.html')
    about_us.content = """<h2>The beginning</h2>

    <p>Smalls Jazz Club was created in 1994 by the enigmatic Mitchell Borden. Borden, a former Navy submariner,
      registered nurse, philosopher & jazz violinist, founded the club with an initiative to create an environment
      that was conducive to Jazz Music and its culture. Borden, who booked and managed the club, approached
      business from a stance of generosity rather than profit. </p>

    <h2>A Club born</h2>

    <p>The original Smalls was a raw basement space and had no liquor license. For just $10, patrons could bring
      their own beer and come to the club at any time, day or night. They could stay as long as they liked and
      often left just as day began to break. Borden’s concern was only with the music and the musicians who
      created it. Under his generous care, a culture of vibrant and newly energized young musicians claimed Smalls
      as their home base and began to develop their individuality in the music. This included such musicians
      as:</p>

    <p>Howard Alden, J.D. Allen, William Ash, Ehud Asherie, Omer Avital, David Berkman, Peter Bernstein, Brian
      Blade, Seamus Blake, Dwayne Burno, Chris Byars, Shard Cassity, Dwayne Clemons, Jay Collins, Marion Cowings,
      Jon Davis, Sasha Dobson, Duane Eubanks, Brian Floody, Joel Frahm, Ray Gallon, Paul Gill, Larry Goldings, Ned
      Goold, Jimmy Greene, Larry Ham, Tardo Hammer, Roy Hargrove, Ari Hoenig, Sherman Irby, Norah Jones, Ryan
      Kisor, Guillermo Klein, Myrna Lake, Carolyn Leonhart, Jason Linder, Joe Magnarelli, Jeremy Manasia, Joe
      Martin, Donny McCauslin, Brad Mehldau, Neal Miner, Tyler Mitchell, Jane Monheit, Mike Mullen, Zaid Nasser,
      Charles Owens, Jeremy Pelt, Sasha Perry, Jean Michel Pilc, Chris Potter, Josh Redman, Jon Roche, Ari Roland,
      Kurt Rosenwinkel, Grant Stewart, Phil Stewart, Joe Strasser, Greg Tardy Mark Turner, Diego Urcola, Richie
      Vitale, Myron Walden, Scott Wendholt, Spike Wilner, Ben Wolfe, Sam Yahel, Peter Zak and many others.</p>"""

    about_us.save()


def add_contact_and_info_content(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    FlatPage = apps.get_model("flatpages", "FlatPage")
    contact = FlatPage.objects.get(template_name='flatpages/contact-and-info.html')
    contact.content = """ <h2>Address:</h2>
    <address>
      183 West 10th Street<br/>
      New York, NY<br/>
      10014 USA
    </address>
    <h2>Email:</h2>
    <p><a href="mailto:smallsjazzclub@gmail.com">smallsjazzclub@gmail.com</a></p>
    <h2>Hours:</h2>
    <p>4.00 PM  -  4.00 AM (EST)</p>
    <h2>Cover:</h2>
    <dl class="prices">
      <dt>$20</dt>
      <dd>(7.30 PM - 12.30 AM)</dd>
      <dt>$10</dt>
      <dd>Afterhours</dd>
      <dt>$10</dt>
      <dd>Students (2nd set only)</dd>
      <dt>$0</dt>
      <dd>Afternoons (1 drink min)</dd>
    </dl>"""

    contact.save()


class Migration(migrations.Migration):
    dependencies = [
        ('static_pages', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_mission_statement_content),
        migrations.RunPython(add_about_us_content),
        migrations.RunPython(add_contact_and_info_content),
    ]
